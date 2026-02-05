"""
Script de teste para verificar se o servidor está carregando credenciais do .env
"""
import os
from dotenv import load_dotenv

# Carregar .env
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, '.env')

print("=" * 80)
print("TESTE DE CARREGAMENTO DO .ENV")
print("=" * 80)
print(f"\nCaminho do .env: {env_path}")
print(f"Arquivo existe: {os.path.exists(env_path)}")
print()

load_dotenv(env_path)

print("Credenciais carregadas:")
print(f"  WEBMAIL_URL: {os.getenv('WEBMAIL_URL', 'NÃO ENCONTRADO')}")
print(f"  EMAIL_LOGIN: {os.getenv('EMAIL_LOGIN', 'NÃO ENCONTRADO')}")
print(f"  EMAIL_SENHA: {'***configurada***' if os.getenv('EMAIL_SENHA') else 'NÃO ENCONTRADO'}")
print()

if os.getenv('WEBMAIL_URL') and os.getenv('EMAIL_LOGIN') and os.getenv('EMAIL_SENHA'):
    print("✅ Todas as credenciais foram carregadas com sucesso!")
else:
    print("❌ Algumas credenciais não foram encontradas!")

print("=" * 80)
