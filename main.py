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
from selenium.common.exceptions import WebDriverException, TimeoutException
import functools

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
                        print(f"❌ Falha após {max_retries} tentativas: {str(e)}")
                        raise e
                    print(f"⚠️ Erro detectado (tentativa {attempt+1}/{max_retries}): {str(e)}")
                    print(f"🔄 Tentando novamente em {delay} segundos...")
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
            print(f"⚠️ Lentidão detectada: Elemento {value} demorou {elapsed:.2f}s")
            
        return element
    except TimeoutException:
        # Se falhar, tentar uma vez com dobro do tempo antes de desistir
        print(f"⚠️ Elemento {value} não encontrado em {timeout}s. Tentando mais {timeout}s...")
        return WebDriverWait(driver, timeout).until(condition((by, value)))



def verificar_e_aguardar_captcha(driver):
    """
    Verifica se há CAPTCHA na página e aguarda resolução manual
    Usa múltiplos métodos de detecção para maior precisão
    
    Args:
        driver: Instância do WebDriver
    """
    print("\n🤖 Verificando se há CAPTCHA...")
    captcha_detectado = False
    
    try:
        # Método 1: Verificar URL
        current_url = driver.current_url
        if "sorry/index" in current_url or "/sorry/" in current_url or "captcha" in current_url.lower():
            captcha_detectado = True
            print("   ⚠️ CAPTCHA detectado via URL")
        
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
                        print(f"   ⚠️ CAPTCHA detectado via texto: '{keyword}'")
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
                        print("   ⚠️ CAPTCHA detectado via iframe reCAPTCHA")
                        break
            except:
                pass
        
    except Exception as e:
        print(f"   ⚠️ Erro ao verificar CAPTCHA: {str(e)}")
    
    if captcha_detectado:
        print("\n" + "=" * 80)
        print("⚠️  CAPTCHA DETECTADO!")
        print("=" * 80)
        print("\n🔐 Por favor, resolva o CAPTCHA manualmente no navegador.")
        input("   Pressione ENTER quando terminar >>> ")
        print("\n✅ Continuando...")
        time.sleep(2)
    else:
        print("   ✅ Nenhum CAPTCHA detectado")


def validar_email(email):
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def fazer_login(driver, url_webmail, email, senha):
    """
    Faz login no Roundcube webmail
    
    Args:
        driver: Instância do WebDriver
        url_webmail: URL do webmail
        email: Email de login
        senha: Senha
        
    Returns:
        bool: True se login bem-sucedido
    """
    try:
        print("\n🌐 Acessando webmail...")
        driver.get(url_webmail)
        
        # Verificar CAPTCHA (que já tem sleep interno se necessário)
        verificar_e_aguardar_captcha(driver)
        
        print("🔐 Fazendo login...")
        
        # Tentar encontrar campos de login (Roundcube)
        try:
            # Espera Inteligente pelo campo de usuário
            user_input = wait_for_element_smart(driver, By.NAME, "_user", timeout=15)
            user_input.clear()
            user_input.send_keys(email)
            
            pass_input = driver.find_element(By.NAME, "_pass")
            pass_input.clear()
            pass_input.send_keys(senha)
            
            driver.find_element(By.ID, "rcm_submit").click()
            
            # Verificar se login foi bem-sucedido
            # Usar wait_for_element_smart para aguardar um elemento pós-login
            WebDriverWait(driver, 15).until(
                EC.url_contains("task=mail") or EC.url_contains("INBOX")
            )
            print("✅ Login realizado com sucesso!")
            return True
                
        except Exception as e:
            print(f"❌ Erro ao localizar campos de login automaticamente: {str(e)}")
            print("💡 Tente fazer login manualmente...")
            input("Pressione ENTER após fazer login manualmente >>> ")
            return True

    except Exception as e:
        print(f"❌ Erro geral ao fazer login: {str(e)}")
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
        print(f"\n📧 Enviando email para: {destinatario}")
        
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
            print("✅ Janela de composição aberta")
        except Exception as e:
            print(f"❌ Erro ao clicar em 'Escrever': {str(e)}")
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
            print(f"✅ Destinatário preenchido: {destinatario}")
        except Exception as e:
            print(f"❌ Erro ao preencher destinatário: {str(e)}")
            return False
        
        # 3. Preencher assunto - XPath fornecido pelo usuário
        try:
            subject_field = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/form/div[1]/div/div[7]/div/input')
            subject_field.clear()
            subject_field.send_keys(assunto)
            print(f"✅ Assunto preenchido: {assunto}")
        except Exception as e:
            print(f"❌ Erro ao preencher assunto: {str(e)}")
            return False
        
        # 4. Preencher mensagem - XPath fornecido pelo usuário
        try:
            body_field = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/form/div[2]/textarea')
            body_field.clear()
            body_field.send_keys(mensagem)
            print("✅ Mensagem preenchida")
        except Exception as e:
            print(f"❌ Erro ao preencher mensagem: {str(e)}")
            return False
        
        # 5. Anexar arquivos (se fornecidos)
        if anexos:
            for anexo in anexos:
                if os.path.exists(anexo):
                    try:
                        print(f"📎 Anexando: {os.path.basename(anexo)}")
                        
                        # Procurar campo de input de arquivo (geralmente hidden)
                        attach_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                        attach_input.send_keys(os.path.abspath(anexo))
                        time.sleep(2)  # Aguardar upload
                        print(f"   ✅ Anexado com sucesso")
                    except Exception as e:
                        print(f"   ⚠️ Erro ao anexar: {str(e)}")
        
        # 6. Enviar email - XPath fornecido pelo usuário
        try:
            send_button = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[2]/div/button')
            send_button.click()
            time.sleep(3)
            print("✅ Email enviado com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro ao enviar email: {str(e)}")
            return False
        
    except Exception as e:
        print(f"❌ Erro geral ao enviar email: {str(e)}")
        return False


def registrar_log(destinatario, assunto, status, pasta_logs="logs"):
    """Registra envio no log"""
    if not os.path.exists(pasta_logs):
        os.makedirs(pasta_logs)
    
    data_hoje = datetime.now().strftime("%Y%m%d")
    arquivo_log = os.path.join(pasta_logs, f"envios_{data_hoje}.txt")
    
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    linha_log = f"[{timestamp}] Para: {destinatario} | Assunto: {assunto} | Status: {status}\n"
    
    with open(arquivo_log, "a", encoding="utf-8") as f:
        f.write(linha_log)


def carregar_lista_emails(arquivo):
    """Carrega lista de emails de um arquivo TXT"""
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return []
    
    with open(arquivo, "r", encoding="utf-8") as f:
        emails = [linha.strip() for linha in f if linha.strip() and validar_email(linha.strip())]
    
    return emails


if __name__ == "__main__":
    print("=" * 80)
    print("  ENVIADOR DE EMAIL AUTOMÁTICO - ROUNDCUBE")
    print("=" * 80)
    print()
    
    # Solicitar credenciais
    print("🔐 CREDENCIAIS DE ACESSO")
    print("-" * 80)
    
    # Tentar carregar do .env primeiro
    url_webmail = os.getenv("WEBMAIL_URL")
    email_login = os.getenv("EMAIL_LOGIN")
    senha_login = os.getenv("EMAIL_SENHA")
    
    # Se não encontrou no .env, solicitar manualmente
    if not url_webmail:
        url_webmail = "https://webmail.instaremail4.com.br/cpsess1913979313/3rdparty/roundcube/?_task=mail&_mbox=INBOX"
        print(f"URL do Webmail: {url_webmail}")
        print("(Pressione ENTER para usar a URL padrão ou digite outra)")
        url_input = input("> ").strip()
        if url_input:
            url_webmail = url_input
    else:
        print(f"✅ URL carregada do .env: {url_webmail}")
    
    if not email_login:
        email_login = input("Email de login: ").strip()
    else:
        print(f"✅ Email carregado do .env: {email_login}")
    
    if not senha_login:
        senha_login = getpass.getpass("Senha: ")
    else:
        print("✅ Senha carregada do .env")
    
    print()
    
    # Menu de opções
    print("📧 MODO DE ENVIO")
    print("-" * 80)
    print("1 - Envio único")
    print("2 - Envio em lote (lista de emails)")
    print("3 - Envio automático (pasta anexos/)")
    print()
    
    opcao = input("Escolha uma opção (1-3): ").strip()
    print()
    
    # Coletar dados específicos do modo ANTES de abrir o navegador
    if opcao == "1":
        # Modo 1: Envio único - coletar todos os dados primeiro
        print("\n📝 DADOS DO EMAIL")
        print("-" * 80)
        destinatario = input("Destinatário: ").strip()
        assunto = input("Assunto: ").strip()
        print("Mensagem (pressione ENTER duas vezes para finalizar):")
        linhas = []
        while True:
            linha = input()
            if linha == "" and linhas and linhas[-1] == "":
                break
            linhas.append(linha)
        mensagem = "\n".join(linhas[:-1])  # Remove última linha vazia
        
        anexo_path = input("Caminho do anexo (deixe vazio para nenhum): ").strip()
        print()
    
    elif opcao == "2":
        # Modo 2: Envio em lote - coletar todos os dados primeiro
        print("\n📝 DADOS DO ENVIO EM LOTE")
        print("-" * 80)
        arquivo_lista = input("Caminho do arquivo com lista de emails: ").strip()
        if not arquivo_lista:
            arquivo_lista = "destinatarios/lista_exemplo.txt"
        
        emails = carregar_lista_emails(arquivo_lista)
        
        if not emails:
            print("❌ Nenhum email válido encontrado na lista.")
            exit(1)
        else:
            print(f"\n✅ {len(emails)} emails carregados.")
            print()
            
            assunto = input("Assunto (mesmo para todos): ").strip()
            print("Mensagem (pressione ENTER duas vezes para finalizar):")
            linhas = []
            while True:
                linha = input()
                if linha == "" and linhas and linhas[-1] == "":
                    break
                linhas.append(linha)
            mensagem = "\n".join(linhas[:-1])
            
            anexo_path = input("Caminho do anexo (deixe vazio para nenhum): ").strip()
            
            print(f"\n⚠️ Você está prestes a enviar {len(emails)} emails.")
            confirma = input("Confirmar envio? (S/N): ").strip().upper()
            
            if confirma != "S":
                print("❌ Envio cancelado.")
                exit(0)
            print()
    
    elif opcao == "3":
        # Modo 3: Envio automático - verificar arquivos e carregar template
        pasta_anexos = "anexos"
        
        if not os.path.exists(pasta_anexos):
            print(f"❌ Pasta '{pasta_anexos}' não encontrada.")
            exit(1)
        
        # Listar arquivos na pasta anexos
        arquivos = [f for f in os.listdir(pasta_anexos) if os.path.isfile(os.path.join(pasta_anexos, f)) and not f.endswith('.md')]
        
        if not arquivos:
            print(f"❌ Nenhum arquivo encontrado na pasta '{pasta_anexos}'.")
            exit(1)
        
        print(f"\n✅ {len(arquivos)} arquivo(s) encontrado(s) na pasta '{pasta_anexos}':")
        for arquivo in arquivos:
            print(f"   📎 {arquivo}")
        print()
        
        # Carregar configuração de email
        config_path = "config/email_template.txt"
        if os.path.exists(config_path):
            print("📋 Carregando template de email...")
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
                
                print(f"✅ Assunto: {assunto_padrao}")
                print(f"✅ Mensagem carregada ({len(mensagem_padrao)} caracteres)")
            except Exception as e:
                print(f"⚠️ Erro ao ler template: {str(e)}")
                assunto_padrao = "Documentos"
                mensagem_padrao = "Segue em anexo."
        else:
            print("⚠️ Arquivo de template não encontrado. Usando padrões...")
            assunto_padrao = input("Assunto (mesmo para todos): ").strip()
            print("Mensagem (pressione ENTER duas vezes para finalizar):")
            linhas = []
            while True:
                linha = input()
                if linha == "" and linhas and linhas[-1] == "":
                    break
                linhas.append(linha)
            mensagem_padrao = "\n".join(linhas[:-1])
        
        print()
        print(f"⚠️ Você está prestes a enviar emails para múltiplos destinatários.")
        print("   Cada arquivo será enviado para o email correspondente ao nome do arquivo.")
        print("   Exemplo: cliente@email.com.pdf → cliente@email.com")
        print()
        confirma = input("Confirmar envio automático? (S/N): ").strip().upper()
        
        if confirma != "S":
            print("❌ Envio cancelado.")
            exit(0)
        print()
    
    # Iniciar navegador
    print("🚀 Iniciando navegador...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    
    try:
        # Fazer login
        if not fazer_login(driver, url_webmail, email_login, senha_login):
            print("❌ Não foi possível fazer login. Encerrando...")
            driver.quit()
            exit(1)
        
        if opcao == "1":
            # Envio único - usar dados já coletados
            sucesso = enviar_email(driver, destinatario, assunto, mensagem, anexo_path if anexo_path else None)
            registrar_log(destinatario, assunto, "SUCESSO" if sucesso else "FALHA")
            
        elif opcao == "2":
            # Envio em lote - usar dados já coletados
            enviados = 0
            falhas = 0
            
            for idx, dest in enumerate(emails, 1):
                print(f"\n[{idx}/{len(emails)}]", end=" ")
                sucesso = enviar_email(driver, dest, assunto, mensagem, anexo_path if anexo_path else None)
                
                if sucesso:
                    enviados += 1
                    registrar_log(dest, assunto, "SUCESSO")
                else:
                    falhas += 1
                    registrar_log(dest, assunto, "FALHA")
                
                # Delay entre envios
                if idx < len(emails):
                    time.sleep(5)
            
            print("\n" + "=" * 80)
            print("📊 RESUMO DE ENVIOS")
            print("=" * 80)
            print(f"✅ Enviados com sucesso: {enviados}")
            print(f"❌ Falhas: {falhas}")
            print(f"📁 Log salvo em: logs/envios_{datetime.now().strftime('%Y%m%d')}.txt")
        
        elif opcao == "3":
            # Envio automático - usar dados já coletados
            enviados = 0
            falhas = 0
            
            # Criar pasta enviados se não existir
            pasta_enviados = "enviados"
            if not os.path.exists(pasta_enviados):
                os.makedirs(pasta_enviados)
            
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
                print(f"\n⚠️ {len(arquivos_invalidos)} arquivo(s) ignorado(s) - nome não é um email válido:")
                for arq in arquivos_invalidos:
                    print(f"   - {arq}")
                print()
            
            total_emails = len(emails_dict)
            print(f"📊 Total de destinatários únicos: {total_emails}")
            print()
            
            # Enviar emails agrupados
            for idx, (destinatario, lista_arquivos) in enumerate(emails_dict.items(), 1):
                caminhos_anexos = [os.path.join(pasta_anexos, arq) for arq in lista_arquivos]
                
                print(f"\n[{idx}/{total_emails}] 📧 {destinatario}")
                print(f"   📎 {len(lista_arquivos)} arquivo(s):")
                for arq in lista_arquivos:
                    print(f"      - {arq}")
                
                sucesso = enviar_email(driver, destinatario, assunto_padrao, mensagem_padrao, caminhos_anexos)
                
                if sucesso:
                    enviados += 1
                    registrar_log(destinatario, assunto_padrao, f"SUCESSO - {len(lista_arquivos)} anexo(s)")
                    
                    # Mover arquivos para pasta enviados
                    for arquivo in lista_arquivos:
                        try:
                            caminho_origem = os.path.join(pasta_anexos, arquivo)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            nome_base, extensao = os.path.splitext(arquivo)
                            novo_nome = f"{nome_base}_{timestamp}{extensao}"
                            destino = os.path.join(pasta_enviados, novo_nome)
                            shutil.move(caminho_origem, destino)
                        except Exception as e:
                            print(f"   ⚠️ Erro ao mover {arquivo}: {str(e)}")
                    
                    print(f"   ✅ Arquivos movidos para: enviados/")
                else:
                    falhas += 1
                    registrar_log(destinatario, assunto_padrao, "FALHA")
                
                # Delay entre envios
                if idx < total_emails:
                    time.sleep(5)
            
            print("\n" + "=" * 80)
            print("📊 RESUMO DE ENVIOS AUTOMÁTICOS")
            print("=" * 80)
            print(f"✅ Emails enviados com sucesso: {enviados}")
            print(f"❌ Falhas: {falhas}")
            print(f"📁 Arquivos enviados movidos para: {pasta_enviados}/")
            print(f"📁 Log salvo em: logs/envios_{datetime.now().strftime('%Y%m%d')}.txt")
        
        print("\n💡 Navegador permanecerá aberto para verificação.")
        input("Pressione ENTER para fechar...")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    finally:
        driver.quit()
        print("🔒 Navegador fechado.")
        print("\n✨ Script finalizado!")
