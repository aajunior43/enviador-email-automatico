"""
Enviador de Email Automático - Roundcube Webmail
Automatiza o login e envio de emails via Roundcube
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from datetime import datetime
import re
import getpass
import shutil
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Verificar se .env foi carregado
if os.getenv("EMAIL_LOGIN"):
    print("[OK] Arquivo .env carregado com sucesso!")
else:
    print("[AVISO] Arquivo .env nao encontrado ou vazio. Credenciais serao solicitadas manualmente.")

from selenium.common.exceptions import WebDriverException, TimeoutException
import functools

# ==========================================
# SISTEMA DE LOGGING PROFISSIONAL
# ==========================================
import logging
from logging.handlers import RotatingFileHandler
import sys

# Configurar diretório de logs
LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Formato do log
log_format = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Handler para arquivo com rotação (máximo 5MB por arquivo, manter 5 backups)
file_handler = RotatingFileHandler(
    os.path.join(LOGS_DIR, 'app.log'),
    maxBytes=5*1024*1024,  # 5MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(log_format)
file_handler.setLevel(logging.DEBUG)

# Handler para console (mantém a experiência do usuário)
class ColoredConsoleHandler(logging.StreamHandler):
    """Handler customizado com cores para o console"""
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'
    }
    
    def emit(self, record):
        # Mapear niveis de log para prefixos
        prefixos = {
            'DEBUG': '[DBG]',
            'INFO': '[INF]',
            'WARNING': '[WRN]',
            'ERROR': '[ERR]',
            'CRITICAL': '[CRT]'
        }
        
        # Adicionar prefixo ao inicio da mensagem
        if not hasattr(record, '_emoji_added'):
            prefixo = prefixos.get(record.levelname, '[---]')
            record.msg = f"{prefixo} {record.msg}"
            record._emoji_added = True
        
        super().emit(record)

console_handler = ColoredConsoleHandler(sys.stdout)
console_handler.setFormatter(log_format)
console_handler.setLevel(logging.INFO)

# Configurar logger raiz
logger = logging.getLogger('EmailAutomation')
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Evitar duplicação de logs
logger.propagate = False

logger.info("=" * 60)
logger.info("SISTEMA DE LOGGING INICIADO")
logger.info("=" * 60)

# Retry decorator
def retry_on_failure(max_retries=3, delay=5):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (WebDriverException, TimeoutException) as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Falha após {max_retries} tentativas: {str(e)}")
                        raise e
                    logger.warning(f"Erro detectado (tentativa {attempt+1}/{max_retries}): {str(e)}")
                    logger.info(f"Tentando novamente em {delay} segundos...")
                    time.sleep(delay)
            return None # Should not reach here
        return wrapper
    return decorator

# Smart wait
def wait_for_element_smart(driver, by, value, timeout=10, condition=EC.presence_of_element_located):
    """
    Espera inteligente que ajusta o timeout se detectar lentidão
    """
    start_time = time.time()
    try:
        # Tentar com timeout padrão
        element = WebDriverWait(driver, timeout).until(condition((by, value)))
        
        # Se demorou mais que 70% do timeout, registrar lentidão (futuro: ajustar dinamicamente)
        elapsed = time.time() - start_time
        if elapsed > (timeout * 0.7):
            logger.warning(f"Lentidão detectada: Elemento {value} demorou {elapsed:.2f}s")
            
        return element
    except TimeoutException:
        # Se falhar, tentar uma vez com dobro do tempo antes de desistir
        logger.warning(f"Elemento {value} não encontrado em {timeout}s. Tentando mais {timeout}s...")
        return WebDriverWait(driver, timeout).until(condition((by, value)))



def verificar_e_aguardar_captcha(driver, modo_gui=False):
    """
    Verifica se há CAPTCHA na página e aguarda resolução manual
    Usa múltiplos métodos de detecção para maior precisão
    
    Args:
        driver: Instância do WebDriver
        modo_gui: Se True, não bloqueia com input() (para uso via interface web)
    """
    logger.info("Verificando se há CAPTCHA...")
    captcha_detectado = False
    
    try:
        # Método 1: Verificar URL
        current_url = driver.current_url
        if "sorry/index" in current_url or "/sorry/" in current_url or "captcha" in current_url.lower():
            captcha_detectado = True
            logger.warning("CAPTCHA detectado via URL")
        
        # Método 2: Procurar por texto comum de CAPTCHA
        if not captcha_detectado:
            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                captcha_keywords = [
                    "unusual traffic", "captcha", "verify you're not a robot",
                    "verify you are not a robot", "i'm not a robot",
                    "prove you're not a robot", "automated queries",
                    "suspicious activity", "tráfego incomum", "tráfego suspeito",
                    "verificar que você não é um robô", "não sou um robô",
                    "consultas automatizadas", "atividade suspeita"
                ]
                
                for keyword in captcha_keywords:
                    if keyword in page_text:
                        captcha_detectado = True
                        logger.warning(f"CAPTCHA detectado via texto: '{keyword}'")
                        break
            except:
                pass
        
        # Método 3: Procurar por iframes do reCAPTCHA
        if not captcha_detectado:
            try:
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    src = iframe.get_attribute("src") or ""
                    if "recaptcha" in src.lower() or "captcha" in src.lower():
                        captcha_detectado = True
                        logger.warning("CAPTCHA detectado via iframe reCAPTCHA")
                        break
            except:
                pass
        
    except Exception as e:
        logger.warning(f"Erro ao verificar CAPTCHA: {str(e)}")
    
    if captcha_detectado:
        logger.critical("=" * 60)
        logger.critical("CAPTCHA DETECTADO!")
        logger.critical("=" * 60)
        logger.info("Por favor, resolva o CAPTCHA manualmente no navegador.")
        
        if not modo_gui:
            # Modo CLI - aguarda input do usuário
            input("   Pressione ENTER quando terminar >>> ")
            logger.info("Continuando...")
        else:
            # Modo GUI - aguarda automaticamente por até 60 segundos
            logger.info("Aguardando resolução do CAPTCHA (60 segundos)...")
            time.sleep(60)
            logger.info("Continuando após aguardar CAPTCHA...")
        
        time.sleep(2)
    else:
        logger.info("Nenhum CAPTCHA detectado")


def validar_email(email):
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def fazer_login(driver, url_webmail, email, senha, modo_gui=False):
    """
    Faz login no Roundcube webmail
    
    Args:
        driver: Instância do WebDriver
        url_webmail: URL do webmail
        email: Email de login
        senha: Senha
        modo_gui: Se True, executa em modo GUI (sem input() bloqueante)
        
    Returns:
        bool: True se login bem-sucedido
    """
    try:
        logger.info("Acessando webmail...")
        driver.get(url_webmail)
        
        # Verificar CAPTCHA (que já tem sleep interno se necessário)
        verificar_e_aguardar_captcha(driver, modo_gui=modo_gui)
        
        logger.info("Fazendo login...")
        
        # Tentar encontrar campos de login com múltiplas estratégias
        user_input = None
        pass_input = None
        submit_button = None
        
        try:
            # Estratégia 1: Roundcube padrão (By.NAME)
            logger.info("Tentando seletores Roundcube padrão...")
            user_input = wait_for_element_smart(driver, By.NAME, "_user", timeout=5)
            pass_input = driver.find_element(By.NAME, "_pass")
            submit_button = driver.find_element(By.ID, "rcm_submit")
            logger.info("Campos encontrados: Roundcube padrão")
            
        except Exception as e1:
            logger.warning(f"Seletores padrão falharam: {str(e1)}")
            
            try:
                # Estratégia 2: XPath personalizado
                logger.info("Tentando seletores XPath personalizados...")
                user_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div[2]/div[2]/form/div[2]/input"))
                )
                pass_input = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div[2]/div[2]/form/div[4]/input")
                
                # Tentar encontrar botão submit por tipo ou texto
                try:
                    submit_button = driver.find_element(By.XPATH, "//button[@type='submit'] | //input[@type='submit']")
                except:
                    submit_button = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/div/div/div[2]/div[2]/form/div[6]/input")
                
                logger.info("Campos encontrados: XPath personalizado")
                
            except Exception as e2:
                logger.error(f"XPath personalizado falhou: {str(e2)}")
                
                # Estratégia 3: Busca genérica por tipo de input
                try:
                    logger.info("Tentando busca genérica por tipo de input...")
                    user_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'], input[type='email']"))
                    )
                    pass_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                    logger.info("Campos encontrados: busca genérica")
                    
                except Exception as e3:
                    logger.error(f"Todas as estratégias falharam: {str(e3)}")
                    raise Exception("Não foi possível localizar os campos de login")
        
        # Preencher e submeter
        if user_input and pass_input and submit_button:
            logger.info("Preenchendo credenciais...")
            user_input.clear()
            user_input.send_keys(email)
            
            pass_input.clear()
            pass_input.send_keys(senha)
            
            logger.info("Clicando em login...")
            submit_button.click()
            
            # Verificar se login foi bem-sucedido
            # Aguardar URL indicando sucesso no login
            try:
                WebDriverWait(driver, 15).until(
                    lambda d: "task=mail" in d.current_url or "INBOX" in d.current_url
                )
                logger.info("Login realizado com sucesso!")
                return True
            except TimeoutException:
                logger.warning("Timeout aguardando redirecionamento pós-login")
                # Verificar se já está na página correta
                if "task=mail" in driver.current_url or "INBOX" in driver.current_url:
                    logger.info("Login realizado com sucesso (verificação manual)!")
                    return True
                raise

    except Exception as e:
        logger.error(f"Erro ao fazer login: {str(e)}")
        return False


@retry_on_failure(max_retries=3)
def enviar_email(driver, destinatario, assunto, mensagem, anexos=None):
    """
    Envia um email via Roundcube
    
    Args:
        driver: Instância do WebDriver
        destinatario: Email do destinatário
        assunto: Assunto do email
        mensagem: Corpo do email
        anexos: Caminho do arquivo ou lista de arquivos para anexar (opcional)
        
    Returns:
        bool: True se enviado com sucesso
    """
    try:
        logger.info(f"Enviando email para: {destinatario}")
        
        # Garantir que anexos seja uma lista
        if anexos is None:
            anexos = []
        elif isinstance(anexos, str):
            anexos = [anexos]
        
        # 1. Clicar em "Escrever" / "Compose" - XPath fornecido pelo usuário
        try:
            compose_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[1]/div[2]/span[1]/a'))
            )
            compose_button.click()
            time.sleep(2)
            logger.info("Janela de composição aberta")
        except Exception as e:
            logger.error(f"Erro ao clicar em 'Escrever': {str(e)}")
            return False
        
        # 2. Preencher destinatário - XPath fornecido pelo usuário
        try:
            to_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/div[2]/form/div[1]/div/div[2]/div/div/ul/li/input'))
            )
            to_field.clear()
            to_field.send_keys(destinatario)
            to_field.send_keys(Keys.ENTER)  # Confirmar o email
            time.sleep(1)
            logger.info(f"Destinatário preenchido: {destinatario}")
        except Exception as e:
            logger.error(f"Erro ao preencher destinatário: {str(e)}")
            return False
        
        # 3. Preencher assunto - XPath fornecido pelo usuário
        try:
            subject_field = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/form/div[1]/div/div[7]/div/input')
            subject_field.clear()
            subject_field.send_keys(assunto)
            logger.info(f"Assunto preenchido: {assunto}")
        except Exception as e:
            logger.error(f"Erro ao preencher assunto: {str(e)}")
            return False
        
        # 4. Preencher mensagem - XPath fornecido pelo usuário
        try:
            body_field = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/form/div[2]/textarea')
            body_field.clear()
            body_field.send_keys(mensagem)
            logger.info("Mensagem preenchida")
        except Exception as e:
            logger.error(f"Erro ao preencher mensagem: {str(e)}")
            return False
        
        # 5. Anexar arquivos (se fornecidos)
        if anexos:
            for anexo in anexos:
                if os.path.exists(anexo):
                    try:
                        logger.info(f"Anexando: {os.path.basename(anexo)}")
                        
                        # Procurar campo de input de arquivo (geralmente hidden)
                        attach_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                        attach_input.send_keys(os.path.abspath(anexo))
                        time.sleep(2)  # Aguardar upload
                        logger.info("Anexado com sucesso")
                    except Exception as e:
                        logger.warning(f"Erro ao anexar: {str(e)}")
        
        # 6. Enviar email - XPath fornecido pelo usuário
        try:
            logger.debug("Procurando botão de enviar...")
            send_button = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/button')
            logger.debug("Botão de enviar encontrado, clicando...")
            send_button.click()
            logger.debug("Aguardando 3 segundos após clique...")
            time.sleep(3)
            logger.info("Email enviado com sucesso!")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            return False
        
    except Exception as e:
        logger.error(f"Erro geral ao enviar email: {str(e)}")
        return False


def registrar_log(destinatario, assunto, status, pasta_logs="logs"):
    """Registra envio no log"""
    if not os.path.exists(pasta_logs):
        os.makedirs(pasta_logs)
        logger.debug(f"Diretório de logs criado: {pasta_logs}")
    
    data_hoje = datetime.now().strftime("%Y%m%d")
    arquivo_log = os.path.join(pasta_logs, f"envios_{data_hoje}.txt")
    
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    linha_log = f"[{timestamp}] Para: {destinatario} | Assunto: {assunto} | Status: {status}\n"
    
    with open(arquivo_log, "a", encoding="utf-8") as f:
        f.write(linha_log)
    
    # Também registrar no logger principal
    if status == "SUCESSO":
        logger.info(f"Email registrado: {destinatario} - {assunto} - {status}")
    else:
        logger.warning(f"Email registrado: {destinatario} - {assunto} - {status}")


def carregar_lista_emails(arquivo):
    """Carrega lista de emails de um arquivo TXT"""
    if not os.path.exists(arquivo):
        logger.error(f"Arquivo não encontrado: {arquivo}")
        return []
    
    with open(arquivo, "r", encoding="utf-8") as f:
        emails = [linha.strip() for linha in f if linha.strip() and validar_email(linha.strip())]
    
    logger.info(f"{len(emails)} emails válidos carregados de {arquivo}")
    return emails


# ==========================================
# FUNCOES DE IMPORTACAO E EXPORTACAO
# ==========================================

def importar_contatos(arquivo):
    """
    Importa contatos de arquivos CSV, Excel (.xlsx) ou TXT
    
    Args:
        arquivo: Caminho do arquivo a ser importado
        
    Returns:
        list: Lista de dicionarios com {'nome': '', 'email': ''}
    """
    if not os.path.exists(arquivo):
        print_error(f"Arquivo não encontrado: {arquivo}")
        return []
    
    extensao = os.path.splitext(arquivo)[1].lower()
    contatos = []
    
    try:
        if extensao == '.csv':
            # Importar CSV
            import csv
            with open(arquivo, 'r', encoding='utf-8') as f:
                # Detectar delimitador
                amostra = f.read(1024)
                f.seek(0)
                sniffer = csv.Sniffer()
                delimitador = sniffer.sniff(amostra).delimiter
                
                reader = csv.DictReader(f, delimiter=delimitador)
                for row in reader:
                    nome = row.get('nome', row.get('name', row.get('NOME', row.get('NAME', '')))).strip()
                    email = row.get('email', row.get('EMAIL', row.get('Email', row.get('e-mail', '')))).strip()
                    
                    if email and validar_email(email):
                        contatos.append({'nome': nome, 'email': email})
                        
        elif extensao in ['.xlsx', '.xls']:
            # Importar Excel
            try:
                import pandas as pd
                df = pd.read_excel(arquivo)
                
                # Detectar colunas de nome e email
                colunas_nome = ['nome', 'name', 'NOME', 'NAME', 'Nome', 'Name']
                colunas_email = ['email', 'EMAIL', 'Email', 'e-mail', 'E-mail', 'E-MAIL']
                
                col_nome = None
                col_email = None
                
                for col in df.columns:
                    if col in colunas_nome:
                        col_nome = col
                    if col in colunas_email:
                        col_email = col
                
                if not col_email:
                    # Tentar encontrar coluna com emails
                    for col in df.columns:
                        if df[col].astype(str).str.contains('@').any():
                            col_email = col
                            break
                
                if not col_email:
                    print_error("Não foi possível identificar a coluna de email no arquivo Excel")
                    return []
                
                for _, row in df.iterrows():
                    nome = str(row.get(col_nome, '')).strip() if col_nome else ''
                    email = str(row.get(col_email, '')).strip()
                    
                    if email and validar_email(email):
                        contatos.append({'nome': nome, 'email': email})
                        
            except ImportError:
                print_error("Biblioteca pandas não instalada. Use: pip install pandas openpyxl")
                return []
                
        elif extensao == '.txt':
            # Importar TXT (um email por linha)
            with open(arquivo, 'r', encoding='utf-8') as f:
                for linha in f:
                    email = linha.strip()
                    if email and validar_email(email):
                        contatos.append({'nome': '', 'email': email})
        else:
            print_error(f"Formato de arquivo não suportado: {extensao}")
            print_info("Formatos suportados: .csv, .xlsx, .xls, .txt")
            return []
        
        print_success(f"{len(contatos)} contato(s) importado(s) com sucesso!")
        logger.info(f"Importados {len(contatos)} contatos de {arquivo}")
        return contatos
        
    except Exception as e:
        print_error(f"Erro ao importar arquivo: {str(e)}")
        logger.error(f"Erro na importação: {str(e)}")
        return []


def exportar_contatos(contatos, arquivo, formato='csv'):
    """
    Exporta contatos para arquivo
    
    Args:
        contatos: Lista de dicionarios {'nome': '', 'email': ''}
        arquivo: Caminho do arquivo de saída
        formato: 'csv', 'excel' ou 'txt'
        
    Returns:
        bool: True se exportado com sucesso
    """
    try:
        if formato.lower() == 'csv':
            import csv
            # Garantir extensão .csv
            if not arquivo.endswith('.csv'):
                arquivo += '.csv'
                
            with open(arquivo, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['nome', 'email'])
                writer.writeheader()
                for contato in contatos:
                    writer.writerow(contato)
                    
        elif formato.lower() in ['excel', 'xlsx']:
            # Garantir extensão .xlsx
            if not arquivo.endswith('.xlsx'):
                arquivo += '.xlsx'
                
            try:
                import pandas as pd
                df = pd.DataFrame(contatos)
                df.to_excel(arquivo, index=False, engine='openpyxl')
            except ImportError:
                print_error("Biblioteca pandas não instalada. Use: pip install pandas openpyxl")
                return False
                
        elif formato.lower() == 'txt':
            # Garantir extensão .txt
            if not arquivo.endswith('.txt'):
                arquivo += '.txt'
                
            with open(arquivo, 'w', encoding='utf-8') as f:
                for contato in contatos:
                    f.write(f"{contato['email']}\n")
        else:
            print_error(f"Formato não suportado: {formato}")
            print_info("Formatos suportados: csv, excel, txt")
            return False
        
        print_success(f"Contatos exportados com sucesso para: {arquivo}")
        logger.info(f"Exportados {len(contatos)} contatos para {arquivo} ({formato})")
        return True
        
    except Exception as e:
        print_error(f"Erro ao exportar: {str(e)}")
        logger.error(f"Erro na exportação: {str(e)}")
        return False


def gerenciar_contatos():
    """
    Menu de gerenciamento de contatos (importar/exportar)
    """
    while True:
        clear_screen()
        print_header("GERENCIAMENTO DE CONTATOS", "Importar e Exportar Listas de Email")
        
        print_section("OPCOES DISPONIVEIS")
        print()
        print_menu_option("1", "Importar Contatos", "Importar de CSV, Excel ou TXT")
        print_menu_option("2", "Exportar Contatos", "Exportar para CSV, Excel ou TXT")
        print_menu_option("3", "Validar Lista de Emails", "Verificar se emails sao validos")
        print_menu_option("4", "Remover Duplicados", "Limpar lista de emails duplicados")
        print_menu_option("0", "Voltar ao Menu Principal")
        print()
        
        opcao = input("  Escolha uma opcao (0-4): ").strip()
        
        if opcao == "0":
            break
            
        elif opcao == "1":
            # Importar contatos
            print_section("IMPORTAR CONTATOS")
            print_info("Formatos suportados: .csv, .xlsx, .xls, .txt")
            arquivo = input("  Caminho do arquivo: ").strip()
            
            if arquivo:
                contatos = importar_contatos(arquivo)
                if contatos:
                    print()
                    print_success(f"Importacao concluida! {len(contatos)} contato(s)")
                    print()
                    print("  Primeiros 5 contatos importados:")
                    for i, c in enumerate(contatos[:5], 1):
                        nome = c['nome'] if c['nome'] else '(sem nome)'
                        print(f"    {i}. {nome} - {c['email']}")
                    
                    if len(contatos) > 5:
                        print(f"    ... e mais {len(contatos) - 5} contato(s)")
                    
                    # Perguntar se deseja salvar lista
                    print()
                    salvar = input("  Deseja salvar a lista em um arquivo? (S/N): ").strip().upper()
                    if salvar == "S":
                        arquivo_saida = input("  Nome do arquivo (ex: contatos_importados): ").strip()
                        if arquivo_saida:
                            formato = input("  Formato (csv/excel/txt): ").strip().lower()
                            if formato in ['csv', 'excel', 'txt']:
                                exportar_contatos(contatos, arquivo_saida, formato)
            
            input("\n  Pressione ENTER para continuar...")
            
        elif opcao == "2":
            # Exportar contatos
            print_section("EXPORTAR CONTATOS")
            
            # Carregar lista existente
            arquivo_origem = input("  Arquivo com a lista de emails: ").strip()
            
            if arquivo_origem and os.path.exists(arquivo_origem):
                contatos = importar_contatos(arquivo_origem)
                
                if contatos:
                    print()
                    print_info("Formatos disponiveis:")
                    print("    - csv: Formato CSV (Excel, Google Sheets)")
                    print("    - excel: Formato Excel (.xlsx)")
                    print("    - txt: Lista simples de emails (.txt)")
                    print()
                    
                    formato = input("  Formato de exportacao (csv/excel/txt): ").strip().lower()
                    
                    if formato in ['csv', 'excel', 'txt']:
                        arquivo_destino = input("  Nome do arquivo de saida: ").strip()
                        if arquivo_destino:
                            exportar_contatos(contatos, arquivo_destino, formato)
            else:
                print_error("Arquivo nao encontrado!")
            
            input("\n  Pressione ENTER para continuar...")
            
        elif opcao == "3":
            # Validar lista
            print_section("VALIDAR LISTA DE EMAILS")
            arquivo = input("  Arquivo com a lista de emails: ").strip()
            
            if arquivo and os.path.exists(arquivo):
                contatos = importar_contatos(arquivo)
                
                if contatos:
                    validos = [c for c in contatos if validar_email(c['email'])]
                    invalidos = [c for c in contatos if not validar_email(c['email'])]
                    
                    print_box("RESULTADO DA VALIDACAO", [
                        f"Total de contatos: {len(contatos)}",
                        f"Emails validos: {len(validos)}",
                        f"Emails invalidos: {len(invalidos)}",
                        f"Taxa de validade: {(len(validos)/len(contatos)*100):.1f}%"
                    ])
                    
                    if invalidos:
                        print()
                        print_warning("Emails invalidos encontrados:")
                        for c in invalidos[:10]:
                            print(f"    - {c['email']}")
                        if len(invalidos) > 10:
                            print(f"    ... e mais {len(invalidos) - 10}")
            else:
                print_error("Arquivo nao encontrado!")
            
            input("\n  Pressione ENTER para continuar...")
            
        elif opcao == "4":
            # Remover duplicados
            print_section("REMOVER DUPLICADOS")
            arquivo = input("  Arquivo com a lista de emails: ").strip()
            
            if arquivo and os.path.exists(arquivo):
                contatos = importar_contatos(arquivo)
                
                if contatos:
                    # Remover duplicados baseado no email
                    emails_vistos = set()
                    unicos = []
                    duplicados = []
                    
                    for c in contatos:
                        email = c['email'].lower()
                        if email not in emails_vistos:
                            emails_vistos.add(email)
                            unicos.append(c)
                        else:
                            duplicados.append(c)
                    
                    print_box("RESULTADO", [
                        f"Total original: {len(contatos)}",
                        f"Contatos unicos: {len(unicos)}",
                        f"Duplicados removidos: {len(duplicados)}"
                    ])
                    
                    if len(duplicados) > 0:
                        salvar = input("\n  Deseja salvar a lista limpa? (S/N): ").strip().upper()
                        if salvar == "S":
                            arquivo_saida = input("  Nome do arquivo (ex: lista_limpa): ").strip()
                            if arquivo_saida:
                                formato = input("  Formato (csv/excel/txt): ").strip().lower()
                                if formato in ['csv', 'excel', 'txt']:
                                    exportar_contatos(unicos, arquivo_saida, formato)
            else:
                print_error("Arquivo nao encontrado!")
            
            input("\n  Pressione ENTER para continuar...")
        else:
            print_error("Opcao invalida!")
            time.sleep(1)


def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title, subtitle=""):
    """Imprime um cabeçalho formatado"""
    width = 70
    print()
    print("=" * width)
    print(f"  {title}")
    if subtitle:
        print(f"  {subtitle}")
    print("=" * width)
    print()

def print_section(title):
    """Imprime uma seção"""
    print()
    print(f">> {title}")
    print("-" * 70)

def print_menu_option(number, title, description=""):
    """Imprime uma opção de menu"""
    if description:
        print(f"  [{number}] {title}")
        print(f"      {description}")
    else:
        print(f"  [{number}] {title}")

def print_success(message):
    """Imprime mensagem de sucesso"""
    print(f"  [OK] {message}")

def print_info(message):
    """Imprime mensagem informativa"""
    print(f"  [INFO] {message}")

def print_warning(message):
    """Imprime aviso"""
    print(f"  [AVISO] {message}")

def print_error(message):
    """Imprime erro"""
    print(f"  [ERRO] {message}")

def print_box(title, lines):
    """Imprime uma caixa com informações"""
    width = max(len(title), max([len(l) for l in lines])) + 4
    print()
    print("+" + "-" * (width - 2) + "+")
    print(f"| {title.center(width - 4)} |")
    print("+" + "-" * (width - 2) + "+")
    for line in lines:
        print(f"| {line.ljust(width - 4)} |")
    print("+" + "-" * (width - 2) + "+")
    print()

def main():
    """Funcao principal do programa"""
    clear_screen()
    
    # Cabeçalho principal
    print_header("ENVIADOR DE EMAIL AUTOMATICO", "Roundcube Webmail Automation Tool")
    
    # Verificar .env
    logger.info("Verificando configuracoes...")
    
    # Solicitar credenciais
    print_section("CONFIGURACAO DE ACESSO")
    
    # Tentar carregar do .env primeiro
    url_webmail = os.getenv("WEBMAIL_URL")
    email_login = os.getenv("EMAIL_LOGIN")
    senha_login = os.getenv("EMAIL_SENHA")
    
    # Se não encontrou no .env, solicitar manualmente
    if not url_webmail:
        url_webmail = "https://webmail.instaremail4.com.br/cpsess1913979313/3rdparty/roundcube/?_task=mail&_mbox=INBOX"
        print(f"  URL do Webmail: {url_webmail}")
        print("  (Pressione ENTER para usar a URL padrao ou digite outra)")
        url_input = input("  > ").strip()
        if url_input:
            url_webmail = url_input
    else:
        print_success(f"URL carregada do .env")
        logger.info(f"URL carregada do .env: {url_webmail}")
    
    if not email_login:
        email_login = input("  Email de login: ").strip()
    else:
        print_success(f"Email carregado do .env: {email_login}")
        logger.info(f"Email carregado do .env: {email_login}")
    
    if not senha_login:
        senha_login = getpass.getpass("  Senha: ")
    else:
        print_success("Senha carregada do .env")
        logger.info("Senha carregada do .env")
    
    # Menu de opções
    print_section("MENU PRINCIPAL")
    print()
    print_menu_option("1", "Envio Unico", "Envia um unico email para um destinatario")
    print_menu_option("2", "Envio em Lote", "Envia o mesmo email para multiplos destinatarios")
    print_menu_option("3", "Envio Automatico", "Envia automaticamente baseado em arquivos na pasta anexos/")
    print_menu_option("4", "Gerenciar Contatos", "Importar/Exportar listas de contatos")
    print_menu_option("0", "Sair", "Encerra o programa")
    print()
    
    opcao = input("  Escolha uma opcao (0-4): ").strip()
    print()
    
    # Opção 0: Sair
    if opcao == "0":
        print_success("Programa encerrado. Ate logo!")
        exit(0)
    
    # Opção 4: Gerenciar Contatos
    elif opcao == "4":
        gerenciar_contatos()
        # Voltar ao inicio do programa
        return
    
    if opcao not in ["1", "2", "3"]:
        print_error("Opcao invalida!")
        time.sleep(2)
        return
    
    # Coletar dados específicos do modo ANTES de abrir o navegador
    if opcao == "1":
        # Modo 1: Envio único - coletar todos os dados primeiro
        print_section("DADOS DO ENVIO UNICO")
        destinatario = input("  Destinatario: ").strip()
        assunto = input("  Assunto: ").strip()
        print("  Mensagem (pressione ENTER duas vezes para finalizar):")
        print("  " + "-" * 50)
        linhas = []
        while True:
            linha = input("  ")
            if linha == "" and linhas and linhas[-1] == "":
                break
            linhas.append(linha)
        mensagem = "\n".join(linhas[:-1])  # Remove última linha vazia
        print("  " + "-" * 50)
        
        anexo_path = input("  Caminho do anexo (deixe vazio para nenhum): ").strip()
        
        print_box("RESUMO DO ENVIO", [
            f"Destinatario: {destinatario}",
            f"Assunto: {assunto}",
            f"Anexo: {anexo_path if anexo_path else 'Nenhum'}"
        ])
    
    elif opcao == "2":
        # Modo 2: Envio em lote - coletar todos os dados primeiro
        print_section("DADOS DO ENVIO EM LOTE")
        arquivo_lista = input("  Caminho do arquivo com lista de emails: ").strip()
        if not arquivo_lista:
            arquivo_lista = "destinatarios/lista_exemplo.txt"
        
        emails = carregar_lista_emails(arquivo_lista)
        
        if not emails:
            print_error("Nenhum email valido encontrado na lista.")
            exit(1)
        else:
            print_success(f"{len(emails)} emails carregados.")
            
            assunto = input("  Assunto (mesmo para todos): ").strip()
            print("  Mensagem (pressione ENTER duas vezes para finalizar):")
            print("  " + "-" * 50)
            linhas = []
            while True:
                linha = input("  ")
                if linha == "" and linhas and linhas[-1] == "":
                    break
                linhas.append(linha)
            mensagem = "\n".join(linhas[:-1])
            print("  " + "-" * 50)
            
            anexo_path = input("  Caminho do anexo (deixe vazio para nenhum): ").strip()
            
            print_box("CONFIRMACAO DE ENVIO EM LOTE", [
                f"Total de destinatarios: {len(emails)}",
                f"Assunto: {assunto}",
                f"Anexo: {anexo_path if anexo_path else 'Nenhum'}",
                "",
                "ATENCAO: Este processo pode levar varios minutos."
            ])
            
            confirma = input("  Confirmar envio? (S/N): ").strip().upper()
            
            if confirma != "S":
                print_warning("Envio cancelado pelo usuario.")
                exit(0)
    
    elif opcao == "3":
        # Modo 3: Envio automático - verificar arquivos e carregar template
        print_section("ENVIO AUTOMATICO")
        pasta_anexos = "anexos"
        
        if not os.path.exists(pasta_anexos):
            print_error(f"Pasta '{pasta_anexos}' nao encontrada.")
            print_info("Crie a pasta 'anexos/' e coloque os arquivos nomeados com o email do destinatario.")
            exit(1)
        
        # Listar arquivos na pasta anexos
        arquivos = [f for f in os.listdir(pasta_anexos) if os.path.isfile(os.path.join(pasta_anexos, f)) and not f.endswith('.md')]
        
        if not arquivos:
            print_error(f"Nenhum arquivo encontrado na pasta '{pasta_anexos}'.")
            exit(1)
        
        print_success(f"{len(arquivos)} arquivo(s) encontrado(s):")
        for i, arquivo in enumerate(arquivos, 1):
            print(f"    {i}. {arquivo}")
        
        # Carregar configuração de email
        config_path = "config/email_template.txt"
        if os.path.exists(config_path):
            print_info("Carregando template de email...")
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                
                # Extrair ASSUNTO
                if "ASSUNTO=" in conteudo:
                    assunto_linha = conteudo.split("ASSUNTO=")[1].split("\n")[0].strip()
                    assunto_padrao = assunto_linha
                else:
                    assunto_padrao = "Documentos"
                
                # Extrair TEXTO (ou MENSAGEM para compatibilidade)
                if "TEXTO=" in conteudo:
                    mensagem_padrao = conteudo.split("TEXTO=")[1].strip()
                elif "MENSAGEM=" in conteudo:
                    mensagem_padrao = conteudo.split("MENSAGEM=")[1].strip()
                else:
                    mensagem_padrao = "Segue em anexo."
                
                print_success(f"Assunto: {assunto_padrao}")
                print_success(f"Mensagem: {len(mensagem_padrao)} caracteres")
            except Exception as e:
                print_warning(f"Erro ao ler template: {str(e)}")
                assunto_padrao = "Documentos"
                mensagem_padrao = "Segue em anexo."
        else:
            print_warning("Arquivo de template nao encontrado. Usando padroes...")
            assunto_padrao = input("  Assunto (mesmo para todos): ").strip()
            print("  Mensagem (pressione ENTER duas vezes para finalizar):")
            print("  " + "-" * 50)
            linhas = []
            while True:
                linha = input("  ")
                if linha == "" and linhas and linhas[-1] == "":
                    break
                linhas.append(linha)
            mensagem_padrao = "\n".join(linhas[:-1])
            print("  " + "-" * 50)
        
        print_box("CONFIRMACAO DE ENVIO AUTOMATICO", [
            f"Total de arquivos: {len(arquivos)}",
            f"Assunto: {assunto_padrao}",
            "",
            "Cada arquivo sera enviado para o email correspondente",
            "ao nome do arquivo.",
            "Exemplo: cliente@email.com.pdf -> cliente@email.com"
        ])
        
        confirma = input("  Confirmar envio automatico? (S/N): ").strip().upper()
        
        if confirma != "S":
            print_warning("Envio cancelado pelo usuario.")
            exit(0)
    
    else:
        print_error("Opcao invalida!")
        exit(1)
    
    # Iniciar navegador
    print_section("INICIALIZACAO")
    print_info("Iniciando navegador Chrome...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    print_success("Navegador iniciado!")
    
    try:
        # Fazer login
        print_info("Realizando login no webmail...")
        if not fazer_login(driver, url_webmail, email_login, senha_login):
            print_error("Nao foi possivel fazer login. Encerrando...")
            driver.quit()
            exit(1)
        print_success("Login realizado com sucesso!")
        
        if opcao == "1":
            # Envio único - usar dados já coletados
            sucesso = enviar_email(driver, destinatario, assunto, mensagem, anexo_path if anexo_path else None)
            registrar_log(destinatario, assunto, "SUCESSO" if sucesso else "FALHA")
            
        elif opcao == "2":
            # Envio em lote - usar dados já coletados
            enviados = 0
            falhas = 0
            
            print_section("ENVIO EM LOTE EM ANDAMENTO")
            print_info(f"Iniciando envio para {len(emails)} destinatarios...")
            print()
            
            for idx, dest in enumerate(emails, 1):
                print(f"  [{idx}/{len(emails)}] Enviando para: {dest}...", end=" ")
                sucesso = enviar_email(driver, dest, assunto, mensagem, anexo_path if anexo_path else None)
                
                if sucesso:
                    enviados += 1
                    registrar_log(dest, assunto, "SUCESSO")
                    print("[OK]")
                else:
                    falhas += 1
                    registrar_log(dest, assunto, "FALHA")
                    print("[FALHA]")
                
                # Delay entre envios
                if idx < len(emails):
                    time.sleep(5)
            
            print()
            print_box("RESUMO DO ENVIO EM LOTE", [
                f"Total de emails: {len(emails)}",
                f"Enviados com sucesso: {enviados}",
                f"Falhas: {falhas}",
                f"Taxa de sucesso: {(enviados/len(emails)*100):.1f}%",
                "",
                f"Log salvo em: logs/envios_{datetime.now().strftime('%Y%m%d')}.txt"
            ])
        
        elif opcao == "3":
            # Envio automático - usar dados já coletados
            enviados = 0
            falhas = 0
            
            # Criar pasta enviados se não existir
            pasta_enviados = "enviados"
            if not os.path.exists(pasta_enviados):
                os.makedirs(pasta_enviados)
                logger.info(f"Pasta 'enviados/' criada: {os.path.abspath(pasta_enviados)}")
            else:
                logger.debug(f"Pasta 'enviados/' já existe: {os.path.abspath(pasta_enviados)}")
            
            # Agrupar arquivos por destinatário
            emails_dict = {}
            arquivos_invalidos = []
            
            for arquivo in arquivos:
                # Extrair email do nome do arquivo
                # Formato: email@dominio.com.extensao ou email@dominio.com-1.extensao
                nome_arquivo = os.path.splitext(arquivo)[0]  # Remove extensão
                
                # Remover sufixos numéricos (ex: -1, -2, etc)
                import re
                nome_limpo = re.sub(r'-\d+$', '', nome_arquivo)
                
                # Validar se é um email
                if validar_email(nome_limpo):
                    if nome_limpo not in emails_dict:
                        emails_dict[nome_limpo] = []
                    emails_dict[nome_limpo].append(arquivo)
                else:
                    arquivos_invalidos.append(arquivo)
            
            if arquivos_invalidos:
                logger.warning(f"{len(arquivos_invalidos)} arquivo(s) ignorado(s) - nome não é um email válido:")
                for arq in arquivos_invalidos:
                    logger.warning(f"   - {arq}")
            
            total_emails = len(emails_dict)
            logger.info(f"Total de destinatários únicos: {total_emails}")
            
            # Enviar emails agrupados
            for idx, (destinatario, lista_arquivos) in enumerate(emails_dict.items(), 1):
                caminhos_anexos = [os.path.join(pasta_anexos, arq) for arq in lista_arquivos]
                
                logger.info(f"[{idx}/{total_emails}] Email: {destinatario}")
                logger.info(f"   -> {len(lista_arquivos)} arquivo(s):")
                for arq in lista_arquivos:
                    logger.info(f"      - {arq}")
                
                logger.debug(f"Chamando enviar_email para {destinatario} com {len(caminhos_anexos)} anexo(s)")
                sucesso = enviar_email(driver, destinatario, assunto_padrao, mensagem_padrao, caminhos_anexos)
                logger.debug(f"Resultado de enviar_email: {sucesso}")
                
                if sucesso:
                    enviados += 1
                    registrar_log(destinatario, assunto_padrao, f"SUCESSO - {len(lista_arquivos)} anexo(s)")
                    logger.info(f"Email enviado com sucesso para {destinatario}. Movendo {len(lista_arquivos)} arquivo(s)...")
                    
                    # Mover arquivos para pasta enviados
                    logger.info(f"Iniciando movimentação de {len(lista_arquivos)} arquivo(s)...")
                    for arquivo in lista_arquivos:
                        try:
                            caminho_origem = os.path.join(pasta_anexos, arquivo)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            nome_base, extensao = os.path.splitext(arquivo)
                            novo_nome = f"{nome_base}_{timestamp}{extensao}"
                            destino = os.path.join(pasta_enviados, novo_nome)
                            
                            # Verificar se arquivo existe antes de mover
                            if not os.path.exists(caminho_origem):
                                logger.error(f"Arquivo não encontrado: {caminho_origem}")
                                continue
                            
                            # Verificar se pasta de destino existe
                            if not os.path.exists(pasta_enviados):
                                os.makedirs(pasta_enviados)
                                logger.info(f"Pasta enviados criada durante movimentação")
                            
                            logger.debug(f"Movendo: {caminho_origem} -> {destino}")
                            shutil.move(caminho_origem, destino)
                            
                            # Verificar se foi movido com sucesso
                            if os.path.exists(destino):
                                logger.info(f"[OK] Arquivo movido com sucesso: {arquivo} -> {novo_nome}")
                            else:
                                logger.error(f"[ERRO] Arquivo nao foi encontrado no destino apos mover: {destino}")
                        except Exception as e:
                            logger.error(f"[ERRO] Erro ao mover arquivo {arquivo}: {str(e)}")
                            logger.debug(f"Caminho origem: {caminho_origem}")
                            logger.debug(f"Caminho destino: {destino}")
                            logger.debug(f"Pasta enviados existe: {os.path.exists(pasta_enviados)}")
                            logger.debug(f"Arquivo origem existe: {os.path.exists(caminho_origem)}")
                    
                    logger.info(f"Processo de movimentação concluído. {len(lista_arquivos)} arquivo(s) processado(s).")
                else:
                    falhas += 1
                    registrar_log(destinatario, assunto_padrao, "FALHA")
                    logger.warning(f"Email NÃO foi enviado para {destinatario}. Arquivos NÃO serão movidos.")
                
                # Delay entre envios
                if idx < total_emails:
                    time.sleep(5)
            
            print()
            print_box("RESUMO DO ENVIO AUTOMATICO", [
                f"Total de destinatarios: {total_emails}",
                f"Emails enviados com sucesso: {enviados}",
                f"Falhas: {falhas}",
                f"Taxa de sucesso: {(enviados/total_emails*100):.1f}%" if total_emails > 0 else "N/A",
                "",
                f"Arquivos movidos para: {pasta_enviados}/",
                f"Log salvo em: logs/envios_{datetime.now().strftime('%Y%m%d')}.txt"
            ])
        
        print()
        print_info("Navegador permanecera aberto para verificacao.")
        input("  Pressione ENTER para fechar o navegador...")
        
    except Exception as e:
        print_error(f"Erro durante a execucao: {str(e)}")
        logger.error(f"Erro: {str(e)}")
    
    finally:
        if driver:
            driver.quit()
            print_success("Navegador fechado.")
        logger.info("Script finalizado!")
        print()
        print("=" * 70)
        print("  Obrigado por usar o Enviador de Email Automatico!")
        print("=" * 70)
        print()


if __name__ == "__main__":
    main()
