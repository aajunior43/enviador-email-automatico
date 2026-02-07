"""
Servidor Web para Interface Gráfica do Enviador de Email Automático
Integra a interface HTML/CSS/JS com o backend Python existente
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime
import threading
from dotenv import load_dotenv
import unicodedata
import re
import time
import shutil
import PyPDF2

# Importar módulo de automação
from email_automation import get_automation_instance, reset_automation_instance

# Adicionar o diretório raiz ao path para importar o main.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurações
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Carregar variáveis de ambiente do arquivo .env
load_dotenv(os.path.join(BASE_DIR, '.env'))

app = Flask(__name__, 
            static_folder='.',
            template_folder='.')
CORS(app)
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
ANEXOS_DIR = os.path.join(BASE_DIR, 'anexos')
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
ENVIADOS_DIR = os.path.join(BASE_DIR, 'enviados')

# Criar diretórios se não existirem
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(ANEXOS_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(ENVIADOS_DIR, exist_ok=True)

TRIAGEM_DIR = os.path.join(BASE_DIR, 'triagem')
os.makedirs(TRIAGEM_DIR, exist_ok=True)

def sanitize_filename(filename):
    """Remove caracteres especiais e acentos do nome do arquivo"""
    # Normalizar para NFKD (separa acentos)
    normalized = unicodedata.normalize('NFKD', filename)
    # Codificar para ASCII ignorando erros (remove acentos)
    ascii_str = normalized.encode('ASCII', 'ignore').decode('ASCII')
    # Remover caracteres não permitidos (manter letras, números, ponto, traço e underscore)
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '', ascii_str)
    return sanitized

def cleanup_logs():
    """Remove logs com mais de 30 dias"""
    try:
        now = time.time()
        days_30 = 30 * 86400
        
        for f in os.listdir(LOGS_DIR):
            path = os.path.join(LOGS_DIR, f)
            if os.path.isfile(path) and f.endswith('.txt'):
                if os.stat(path).st_mtime < (now - days_30):
                    os.remove(path)
                    print(f"🧹 Log antigo removido: {f}")
    except Exception as e:
        print(f"[AVISO] Erro ao limpar logs: {e}")

# Executar limpeza de logs no início
cleanup_logs()

# Variável global para progresso
progress_stats = {
    'total': 0,
    'current': 0,
    'status': 'idle', # idle, running, completed, error
    'message': ''
}


@app.route('/')
def index():
    """Página principal"""
    return send_from_directory('.', 'index.html')


@app.route('/styles.css')
def styles():
    """CSS"""
    return send_from_directory('.', 'styles.css')


@app.route('/script.js')
def script():
    """JavaScript"""
    return send_from_directory('.', 'script.js')


def load_email_template():
    """Carrega o template de email do arquivo config/email_template.txt"""
    template_path = os.path.join(BASE_DIR, 'config', 'email_template.txt')
    subject = ''
    message = ''
    
    try:
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extrair assunto (primeira linha que começa com ASSUNTO=)
            lines = content.split('\n')
            text_started = False
            text_lines = []
            
            for line in lines:
                if line.startswith('ASSUNTO='):
                    subject = line.replace('ASSUNTO=', '').strip()
                elif line.startswith('TEXTO='):
                    text_started = True
                    text_lines.append(line.replace('TEXTO=', '').strip())
                elif text_started:
                    text_lines.append(line.rstrip('\r'))
            
            message = '\n'.join(text_lines)
    except Exception as e:
        print(f"[AVISO] Erro ao carregar template: {e}")
    
    return subject, message


@app.route('/api/credentials', methods=['GET'])
def get_credentials():
    """Retorna as credenciais do arquivo .env e template de email"""
    try:
        # Carregar template de email
        subject, message = load_email_template()
        
        credentials = {
            'url': os.getenv('WEBMAIL_URL', 'https://webmail.instaremail4.com.br/cpsess1913979313/3rdparty/roundcube/?_task=mail&_mbox=INBOX'),
            'email': os.getenv('EMAIL_LOGIN', ''),
            'hasPassword': bool(os.getenv('EMAIL_SENHA')),
            'defaultSubject': subject,
            'defaultMessage': message
        }
        
        return jsonify({
            'success': True,
            'credentials': credentials
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao carregar credenciais: {str(e)}'
        }), 500


@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """Testa a conexão com o webmail fazendo login real"""
    try:
        data = request.json
        url = data.get('url')
        email = data.get('email')
        password = data.get('password')
        
        # Se senha não foi fornecida, tentar usar do .env
        if not password:
            password = os.getenv('EMAIL_SENHA')
        
        # Validações básicas
        if not all([url, email, password]):
            return jsonify({
                'success': False,
                'message': 'Todos os campos são obrigatórios (ou configure no .env)'
            }), 400
        
        # Fazer login real no webmail
        automation = get_automation_instance()
        sucesso = automation.fazer_login_webmail(url, email, password)
        
        if sucesso:
            return jsonify({
                'success': True,
                'message': 'Login realizado com sucesso! Navegador aberto e pronto para enviar emails.'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Falha no login. Verifique suas credenciais.'
            }), 401
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao testar conexão: {str(e)}'
        }), 500


@app.route('/api/send-email', methods=['POST'])
def send_email():
    """Envia email(s) baseado no modo selecionado"""
    try:
        data = request.json
        mode = data.get('mode')
        credentials = data.get('credentials')
        
        if mode == 'single':
            return send_single_email(data, credentials)
        elif mode == 'batch':
            return send_batch_emails(data, credentials)
        elif mode == 'auto':
            return send_auto_emails(data, credentials)
        elif mode == 'send-to-contacts':
            return send_batch_emails(data, credentials)
        else:
            return jsonify({
                'success': False,
                'message': 'Modo inválido'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao enviar email: {str(e)}'
        }), 500


def send_single_email(data, credentials):
    """Envia um único email usando automação real"""
    try:
        recipient = data.get('recipient')
        subject = data.get('subject')
        message = data.get('message')
        
        # Se senha não foi fornecida nas credenciais, usar do .env
        if credentials and not credentials.get('password'):
            credentials['password'] = os.getenv('EMAIL_SENHA')
        
        # Obter instância de automação
        automation = get_automation_instance()
        
        # Verificar se está logado
        if not automation.logged_in:
            # Fazer login primeiro
            url = credentials.get('url') or os.getenv('WEBMAIL_URL')
            email = credentials.get('email') or os.getenv('EMAIL_LOGIN')
            password = credentials.get('password') or os.getenv('EMAIL_SENHA')
            
            if not automation.fazer_login_webmail(url, email, password):
                return jsonify({
                    'success': False,
                    'message': 'Falha ao fazer login no webmail'
                }), 401
        
        # Enviar email real
        sucesso = automation.enviar_email_unico(recipient, subject, message)
        
        if sucesso:
            return jsonify({
                'success': True,
                'message': 'Email enviado com sucesso!',
                'recipient': recipient
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Falha ao enviar email. Verifique os logs.'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao enviar email: {str(e)}'
        }), 500


def send_batch_emails(data, credentials):
    """Envia emails em lote com atualização de progresso"""
    global progress_stats
    try:
        recipients = data.get('recipients', [])
        subject = data.get('subject')
        message = data.get('message')
        
        # Resetar stats
        progress_stats['total'] = len(recipients)
        progress_stats['current'] = 0
        progress_stats['status'] = 'running'
        progress_stats['message'] = 'Iniciando envio em lote...'
        
        if not recipients:
             return jsonify({'success': False, 'message': 'Lista de destinatários vazia'}), 400
        
        # Se senha não foi fornecida nas credenciais, usar do .env
        if credentials and not credentials.get('password'):
            credentials['password'] = os.getenv('EMAIL_SENHA')
        
        # Obter instância de automação
        automation = get_automation_instance()
        
        # Verificar se está logado
        if not automation.logged_in:
            progress_stats['message'] = 'Fazendo login no webmail...'
            # Fazer login primeiro
            url = credentials.get('url') or os.getenv('WEBMAIL_URL')
            email = credentials.get('email') or os.getenv('EMAIL_LOGIN')
            password = credentials.get('password') or os.getenv('EMAIL_SENHA')
            
            if not automation.fazer_login_webmail(url, email, password):
                progress_stats['status'] = 'error'
                progress_stats['message'] = 'Falha no login'
                return jsonify({
                    'success': False,
                    'message': 'Falha ao fazer login no webmail'
                }), 401
        
        # Loop manual para controle de progresso
        enviados = 0
        falhas = 0
        
        for i, dest in enumerate(recipients, 1):
            progress_stats['current'] = i
            progress_stats['message'] = f'Enviando para {dest}...'
            
            # TODO: suportar anexos em lote (data.get('files')) se necessário, por enquanto None
            sucesso = automation.enviar_email_unico(dest, subject, message)
            
            if sucesso:
                enviados += 1
            else:
                falhas += 1
            
            # Pequeno delay entre envios
            if i < len(recipients):
                time.sleep(2) # Reduzido para 2s para ser mais rápido
        
        progress_stats['status'] = 'completed'
        progress_stats['message'] = 'Envio concluído!'
        
        return jsonify({
            'success': True,
            'message': f'{enviados} emails enviados com sucesso',
            'sent': enviados,
            'failed': falhas
        })
        
    except Exception as e:
        progress_stats['status'] = 'error'
        progress_stats['message'] = f'Erro: {str(e)}'
        return jsonify({
            'success': False,
            'message': f'Erro ao enviar emails em lote: {str(e)}'
        }), 500


def send_auto_emails(data, credentials):
    """Envia emails automaticamente baseado em arquivos"""
    global progress_stats
    try:
        subject = data.get('subject')
        message = data.get('message')
        
        # Listar arquivos na pasta anexos
        if not os.path.exists(ANEXOS_DIR):
            return jsonify({
                'success': False,
                'message': 'Pasta anexos/ não encontrada'
            }), 404
        
        files = [f for f in os.listdir(ANEXOS_DIR) 
                if os.path.isfile(os.path.join(ANEXOS_DIR, f)) and not f.endswith('.md')]
        
        if not files:
            return jsonify({
                'success': False,
                'message': 'Nenhum arquivo encontrado na pasta anexos/'
            }), 404
        
        # Configurar stats
        progress_stats['total'] = len(files)
        progress_stats['current'] = 0
        progress_stats['status'] = 'running'
        progress_stats['message'] = 'Iniciando envio automático...'
        
        sent_count = 0
        failed_count = 0
        
        log_file = os.path.join(LOGS_DIR, f"envios_{datetime.now().strftime('%Y%m%d')}.txt")
        
        # Processar cada arquivo
        for i, file in enumerate(files, 1):
            try:
                progress_stats['current'] = i
                
                # Extrair email do nome do arquivo
                filename = os.path.splitext(file)[0]
                # Remover sufixos numéricos
                import re
                recipient = re.sub(r'-\d+$', '', filename)
                
                progress_stats['message'] = f'Processando {file}...'
                
                # Validar email
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', recipient):
                    continue
                
                # Obter instância de automação
                automation = get_automation_instance()
                
                # Verificar se está logado
                if not automation.logged_in:
                    progress_stats['message'] = 'Fazendo login...'
                    # Fazer login primeiro
                    url = credentials.get('url') or os.getenv('WEBMAIL_URL')
                    email = credentials.get('email') or os.getenv('EMAIL_LOGIN')
                    password = credentials.get('password') or os.getenv('EMAIL_SENHA')
                    
                    if not automation.fazer_login_webmail(url, email, password):
                         progress_stats['status'] = 'error'
                         progress_stats['message'] = 'Falha no login'
                         return jsonify({
                            'success': False,
                            'message': 'Falha ao fazer login no webmail'
                        }), 401
                
                # Caminho completo do anexo
                file_path = os.path.join(ANEXOS_DIR, file)
                
                progress_stats['message'] = f'Enviando para {recipient}...'
                
                # Enviar email com anexo
                sucesso = automation.enviar_email_unico(recipient, subject, message, [file_path])
                
                if sucesso:
                    sent_count += 1
                    with open(log_file, 'a') as f:
                        f.write(f"{datetime.now()}: SUCESSO - {recipient} - {file}\n")
                    
                    # MOVER ARQUIVO PARA PASTA ENVIADOS
                    try:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename_base, ext = os.path.splitext(file)
                        novo_nome = f"{filename_base}_{timestamp}{ext}"
                        destino = os.path.join(ENVIADOS_DIR, novo_nome)
                        
                        if os.path.exists(file_path):
                            shutil.move(file_path, destino)
                            print(f"[OK] Arquivo movido: {file} -> enviados/{novo_nome}")
                        else:
                            print(f"[AVISO] Arquivo nao encontrado para mover: {file_path}")
                    except Exception as move_error:
                        print(f"[ERRO] Erro ao mover arquivo {file}: {str(move_error)}")
                else:
                    failed_count += 1
                    with open(log_file, 'a') as f:
                        f.write(f"{datetime.now()}: FALHA - {recipient} - {file}\n")
                
                # Pequeno delay entre envios
                time.sleep(2)
                
            except Exception as e:
                failed_count += 1
                with open(log_file, 'a') as f:
                    f.write(f"{datetime.now()}: ERRO - {file} - {str(e)}\n")
        
        progress_stats['status'] = 'completed'
        progress_stats['message'] = 'Processamento concluído!'
        
        return jsonify({
            'success': True,
            'message': f'Processamento concluído. Enviados: {sent_count}, Falhas: {failed_count}',
            'stats': {
                'sent': sent_count,
                'failed': failed_count
            }
        })
    except Exception as e:
        progress_stats['status'] = 'error'
        progress_stats['message'] = f'Erro: {str(e)}'
        return jsonify({
            'success': False,
            'message': f'Erro ao enviar emails automáticos: {str(e)}'
        }), 500


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Retorna os logs de envio"""
    try:
        date = request.args.get('date', datetime.now().strftime('%Y%m%d'))
        log_file = os.path.join(LOGS_DIR, f"envios_{date}.txt")
        
        if not os.path.exists(log_file):
            return jsonify({
                'success': False,
                'message': 'Nenhum log encontrado para esta data'
            }), 404
        
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = f.readlines()
        
        return jsonify({
            'success': True,
            'logs': logs,
            'count': len(logs)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao carregar logs: {str(e)}'
        }), 500


@app.route('/api/files', methods=['GET'])
def get_files():
    """Lista arquivos na pasta anexos"""
    try:
        if not os.path.exists(ANEXOS_DIR):
            return jsonify({
                'success': True,
                'files': []
            })
        
        files = []
        for f in os.listdir(ANEXOS_DIR):
            if os.path.isfile(os.path.join(ANEXOS_DIR, f)) and not f.endswith('.md'):
                file_path = os.path.join(ANEXOS_DIR, f)
                files.append({
                    'name': f,
                    'size': os.path.getsize(file_path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%d/%m/%Y %H:%M:%S')
                })
        
        return jsonify({
            'success': True,
            'files': files,
            'count': len(files)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar arquivos: {str(e)}'
        }), 500


@app.route('/api/close-browser', methods=['POST'])
def close_browser():
    """Fecha o navegador e encerra a sessão"""
    try:
        reset_automation_instance()
        return jsonify({
            'success': True,
            'message': 'Navegador fechado com sucesso'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao fechar navegador: {str(e)}'
        }), 500


# ==========================================
# ENDPOINTS DE TRIAGEM
# ==========================================

# Definir TRIAGEM_DIR (assumindo que BASE_DIR já está definido)
# Se BASE_DIR não estiver definido, esta linha causará um erro.
# Por favor, certifique-se de que BASE_DIR está definido no início do seu arquivo.
TRIAGEM_DIR = os.path.join(BASE_DIR, 'triagem')
os.makedirs(TRIAGEM_DIR, exist_ok=True)


@app.route('/api/triagem/files', methods=['GET'])
def list_triagem_files():
    """Lista arquivos na pasta triagem"""
    try:
        if not os.path.exists(TRIAGEM_DIR):
            return jsonify({'success': False, 'message': 'Pasta triagem não encontrada'}), 404
            
        files = []
        for f in os.listdir(TRIAGEM_DIR):
            path = os.path.join(TRIAGEM_DIR, f)
            if os.path.isfile(path) and not f.startswith('.'):
                files.append(f)
                
        return jsonify({
            'success': True,
            'files': sorted(files)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/triagem/file/<path:filename>')
def serve_triagem_file(filename):
    """Serve um arquivo da pasta triagem para visualização"""
    return send_from_directory(TRIAGEM_DIR, filename)


@app.route('/api/triagem/scan', methods=['POST'])
def scan_triagem_file():
    """Lê o PDF e tenta encontrar um email"""
    try:
        data = request.json
        filename = data.get('filename')
        
        if not filename:
             return jsonify({'success': False, 'message': 'Nome do arquivo não fornecido'}), 400

        path = os.path.join(TRIAGEM_DIR, filename)
        
        if not os.path.exists(path):
            return jsonify({'success': False, 'message': 'Arquivo não encontrado'}), 404
            
        emails = []
        
        try:
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                # Ler apenas a primeira página para performance
                if len(reader.pages) > 0:
                    text = reader.pages[0].extract_text()
                    # Regex para encontrar emails
                    found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
                    if found:
                        emails = list(set(found)) # Remover duplicatas
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao ler PDF: {str(e)}'}), 500
            
        if emails:
            return jsonify({'success': True, 'email': emails[0], 'all_emails': emails, 'message': f'Email encontrado: {emails[0]}'})
        else:
            return jsonify({'success': False, 'message': 'Nenhum email detectado no PDF'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/triagem/process', methods=['POST'])
def process_triagem_file():
    """Renomeia e move arquivo(s) da triagem para anexos"""
    try:
        data = request.json
        # Suportar tanto 'files' (lista) quanto 'filename' (string única - legado)
        files_to_process = data.get('files', [])
        if not files_to_process and data.get('filename'):
            files_to_process = [data.get('filename')]
            
        email = data.get('email')
        
        if not files_to_process or not email:
            return jsonify({'success': False, 'message': 'Selecione arquivos e informe o email'}), 400
            
        # Validar email
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
             return jsonify({'success': False, 'message': 'Email inválido'}), 400
             
        processed_count = 0
        errors = []
        
        for original_filename in files_to_process:
            try:
                source_path = os.path.join(TRIAGEM_DIR, original_filename)
                
                if not os.path.exists(source_path):
                    errors.append(f"{original_filename}: Arquivo não encontrado")
                    continue
                
                # Manter extensão original
                _, ext = os.path.splitext(original_filename)
                
                # Gerar nome com sufixo incremental para evitar sobrescrita
                # Tenta email.ext, depois email-1.ext, email-2.ext, etc.
                
                # Verificando se já existe o arquivo base (sem sufixo numérico explícito)
                # O padrão do script main.py aceita email.ext ou email-N.ext
                
                candidate_name = f"{email}{ext}"
                dest_path = os.path.join(ANEXOS_DIR, candidate_name)
                
                if os.path.exists(dest_path):
                    counter = 1
                    while True:
                        candidate_name = f"{email}-{counter}{ext}"
                        dest_path = os.path.join(ANEXOS_DIR, candidate_name)
                        if not os.path.exists(dest_path):
                            break
                        counter += 1
                
                # Mover (renomear) com proteção
                import shutil
                shutil.move(source_path, dest_path)
                processed_count += 1
                
            except PermissionError:
                errors.append(f"{original_filename}: Arquivo em uso")
            except Exception as e:
                errors.append(f"{original_filename}: {str(e)}")
        
        if processed_count == 0 and errors:
            return jsonify({'success': False, 'message': 'Erros: ' + '; '.join(errors)}), 500
            
        if errors:
            msg = f'{processed_count} arquivos processados. Erros: {"; ".join(errors)}'
        else:
            msg = f'{processed_count} arquivos movidos para envio.'
            
        return jsonify({
            'success': True,
            'message': msg
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/triagem/upload', methods=['POST'])
def upload_triagem():
    """Recebe upload de arquivos para a pasta triagem"""
    # ... (código existente)

# ==========================================
# GESTÃO DE CONTATOS
# ==========================================
CONTACTS_FILE = os.path.join(BASE_DIR, 'gui', 'contacts.json') # Ajuste: gui/contacts.json

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Lista todos os contatos"""
    try:
        if os.path.exists(CONTACTS_FILE):
            with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
                contacts = json.load(f)
        else:
            contacts = []
        return jsonify(contacts)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/contacts', methods=['POST'])
def add_contact():
    """Adiciona um novo contato"""
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        
        if not name or not email:
            return jsonify({'success': False, 'message': 'Nome e email são obrigatórios'}), 400
            
        contacts = []
        if os.path.exists(CONTACTS_FILE):
            with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
                contacts = json.load(f)
        
        # Verificar duplicatas
        for c in contacts:
            if c['email'] == email:
                return jsonify({'success': False, 'message': 'Email já cadastrado'}), 400
                
        contacts.append({'name': name, 'email': email})
        
        with open(CONTACTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(contacts, f, ensure_ascii=False, indent=2)
            
        return jsonify({'success': True, 'message': 'Contato adicionado'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/contacts/<email>', methods=['DELETE'])
def delete_contact(email):
    """Remove um contato"""
    try:
        if not os.path.exists(CONTACTS_FILE):
             return jsonify({'success': False, 'message': 'Arquivo de contatos não encontrado'}), 404
             
        with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
            contacts = json.load(f)
            
        new_contacts = [c for c in contacts if c['email'] != email]
        
        if len(new_contacts) == len(contacts):
            return jsonify({'success': False, 'message': 'Contato não encontrado'}), 404
            
        with open(CONTACTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_contacts, f, ensure_ascii=False, indent=2)
            
        return jsonify({'success': True, 'message': 'Contato removido'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

    try:
        if 'files[]' not in request.files:
             return jsonify({'success': False, 'message': 'Nenhum arquivo enviado'}), 400
        
        uploaded_files = request.files.getlist('files[]')
        saved_count = 0
        
        for file in uploaded_files:
            if file.filename:
                # Sanitizar nome
                filename = sanitize_filename(file.filename)
                
                # Garantir nome único se já existir
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(os.path.join(TRIAGEM_DIR, filename)):
                    filename = f"{base}_{counter}{ext}"
                    counter += 1
                
                file.save(os.path.join(TRIAGEM_DIR, filename))
                saved_count += 1
                
        return jsonify({'success': True, 'message': f'{saved_count} arquivos enviados para triagem'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/progress', methods=['GET'])
def get_progress():
    """Retorna o status atual do progresso"""
    global progress_stats
    return jsonify(progress_stats)

def open_browser():
    """Abre o navegador automaticamente"""
    import webbrowser
    import time
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')


@app.route('/api/reports/daily', methods=['GET'])
def generate_daily_report():
    """Gera relatório PDF dos envios de hoje"""
    try:
        from fpdf import FPDF
        
        today_str = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(LOGS_DIR, f'envios_{today_str}.txt')
        
        if not os.path.exists(log_file):
            return jsonify({'success': False, 'message': 'Nenhum log encontrado para hoje'}), 404
            
        # Ler logs
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Gerar PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16)
        pdf.cell(200, 10, txt=f"Relatório de Envios - {datetime.now().strftime('%d/%m/%Y')}", ln=1, align="C")
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt=f"Gerado em: {datetime.now().strftime('%H:%M:%S')}", ln=1, align="C")
        pdf.ln(10)
        
        pdf.set_font("Courier", size=10) # Courier para alinhar melhor logs
        for line in lines:
            # Limpar caracteres incompatíveis
            safe_line = line.strip().encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 6, txt=safe_line, ln=1)
            
        # Salvar temporário
        report_filename = f'Relatorio_{today_str}.pdf'
        report_path = os.path.join(BASE_DIR, report_filename)
        pdf.output(report_path)
        
        return send_file(report_path, as_attachment=True, download_name=report_filename)
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    print("=" * 80)
    print("  ENVIADOR DE EMAIL AUTOMÁTICO - INTERFACE WEB")
    print("=" * 80)
    print()
    print("Servidor iniciando em: http://localhost:5000")
    print("Diretorio base:", BASE_DIR)
    print()
    print("Abrindo navegador...")
    print()
    
    # Abrir navegador em uma thread separada
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Iniciar servidor Flask
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
