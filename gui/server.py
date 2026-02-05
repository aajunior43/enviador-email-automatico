"""
Servidor Web para Interface Gráfica do Enviador de Email Automático
Integra a interface HTML/CSS/JS com o backend Python existente
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import json
from datetime import datetime
import threading
from dotenv import load_dotenv

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

# Criar diretórios se não existirem
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(ANEXOS_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

TRIAGEM_DIR = os.path.join(BASE_DIR, 'triagem')
os.makedirs(TRIAGEM_DIR, exist_ok=True)


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
        print(f"⚠️ Erro ao carregar template: {e}")
    
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
    """Envia emails em lote usando automação real"""
    try:
        recipients = data.get('recipients', [])
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
        
        # Enviar emails em lote
        resultado = automation.enviar_emails_lote(recipients, subject, message)
        
        return jsonify({
            'success': True,
            'message': f'{resultado["enviados"]} emails enviados com sucesso',
            'sent': resultado['enviados'],
            'failed': resultado['falhas']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao enviar emails em lote: {str(e)}'
        }), 500


def send_auto_emails(data, credentials):
    """Envia emails automaticamente baseado em arquivos"""
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
        
        sent_count = 0
        failed_count = 0
        
        log_file = os.path.join(LOGS_DIR, f"envios_{datetime.now().strftime('%Y%m%d')}.txt")
        
        # Processar cada arquivo
        for file in files:
            try:
                # Extrair email do nome do arquivo
                filename = os.path.splitext(file)[0]
                # Remover sufixos numéricos
                import re
                recipient = re.sub(r'-\d+$', '', filename)
                
                # Validar email
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', recipient):
                    continue
                
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
                
                # Caminho completo do anexo
                file_path = os.path.join(ANEXOS_DIR, file)
                
                # Enviar email com anexo
                sucesso = automation.enviar_email_unico(recipient, subject, message, [file_path])
                
                if sucesso:
                    sent_count += 1
                    with open(log_file, 'a') as f:
                        f.write(f"{datetime.now()}: SUCESSO - {recipient} - {file}\n")
                else:
                    failed_count += 1
                    with open(log_file, 'a') as f:
                        f.write(f"{datetime.now()}: FALHA - {recipient} - {file}\n")
                
                # Pequeno delay entre envios
                time.sleep(2)
                
            except Exception as e:
                failed_count += 1
        
        return jsonify({
            'success': True,
            'message': f'{sent_count} emails enviados automaticamente',
            'sent': sent_count,
            'failed': failed_count
        })
        
    except Exception as e:
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


@app.route('/api/triagem/process', methods=['POST'])
def process_triagem_file():
    """Renomeia e move arquivo da triagem para anexos"""
    try:
        data = request.json
        original_filename = data.get('filename')
        email = data.get('email')
        
        if not original_filename or not email:
            return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
            
        # Validar email
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
             return jsonify({'success': False, 'message': 'Email inválido'}), 400
             
        # Construir nomes
        source_path = os.path.join(TRIAGEM_DIR, original_filename)
        
        # Manter extensão original
        _, ext = os.path.splitext(original_filename)
        new_filename = f"{email}{ext}"
        dest_path = os.path.join(ANEXOS_DIR, new_filename)
        
        if not os.path.exists(source_path):
            return jsonify({'success': False, 'message': 'Arquivo original não encontrado'}), 404
            
        # Mover (renomear)
        import shutil
        shutil.move(source_path, dest_path)
        
        return jsonify({
            'success': True,
            'message': f'Arquivo processado: {new_filename}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def open_browser():
    """Abre o navegador automaticamente"""
    import webbrowser
    import time
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')


if __name__ == '__main__':
    print("=" * 80)
    print("  ENVIADOR DE EMAIL AUTOMÁTICO - INTERFACE WEB")
    print("=" * 80)
    print()
    print("🌐 Servidor iniciando em: http://localhost:5000")
    print("📁 Diretório base:", BASE_DIR)
    print()
    print("✨ Abrindo navegador...")
    print()
    
    # Abrir navegador em uma thread separada
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Iniciar servidor Flask
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
