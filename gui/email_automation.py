"""
Módulo de integração entre a interface web e o código de automação Selenium
Importa e usa as funções do main.py para envio real de emails
"""

import sys
import os
import logging

# Configurar logger
logger = logging.getLogger('EmailAutomation.GUI')

# Adicionar diretório pai ao path para importar main.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Importar funções do main.py
try:
    from main import fazer_login, enviar_email, registrar_log, validar_email
except ImportError as e:
    logger.error(f"Erro ao importar funções do main.py: {e}")
    fazer_login = None
    enviar_email = None
    registrar_log = None
    validar_email = None


class EmailAutomation:
    """Classe para gerenciar a automação de emails via interface web"""
    
    def __init__(self):
        self.driver = None
        self.logged_in = False
        
    def iniciar_navegador(self):
        """Inicia o navegador Chrome"""
        if self.driver is None:
            logger.info("Iniciando navegador Chrome...")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service)
            self.driver.maximize_window()
            return True
        return True
    
    def fazer_login_webmail(self, url, email, senha):
        """Faz login no webmail usando a função do main.py"""
        if not self.iniciar_navegador():
            return False
        
        if fazer_login:
            self.logged_in = fazer_login(self.driver, url, email, senha, modo_gui=True)
            return self.logged_in
        else:
            logger.error("Função fazer_login não disponível")
            return False
    
    def enviar_email_unico(self, destinatario, assunto, mensagem, anexos=None):
        """Envia um único email usando a função do main.py"""
        if not self.logged_in:
            logger.error("Não está logado no webmail")
            return False
        
        if enviar_email:
            sucesso = enviar_email(self.driver, destinatario, assunto, mensagem, anexos)
            
            if registrar_log:
                registrar_log(destinatario, assunto, "SUCESSO" if sucesso else "FALHA")
            
            return sucesso
        else:
            logger.error("Função enviar_email não disponível")
            return False
    
    def enviar_emails_lote(self, destinatarios, assunto, mensagem, anexos=None):
        """Envia emails em lote"""
        if not self.logged_in:
            logger.error("Não está logado no webmail")
            return {'enviados': 0, 'falhas': 0}
        
        enviados = 0
        falhas = 0
        
        for idx, dest in enumerate(destinatarios, 1):
            logger.info(f"[{idx}/{len(destinatarios)}] Enviando para: {dest}")
            
            if enviar_email:
                sucesso = enviar_email(self.driver, dest, assunto, mensagem, anexos)
                
                if sucesso:
                    enviados += 1
                else:
                    falhas += 1
                
                if registrar_log:
                    registrar_log(dest, assunto, "SUCESSO" if sucesso else "FALHA")
                
                # Delay entre envios
                if idx < len(destinatarios):
                    time.sleep(5)
            else:
                logger.error("Função enviar_email não disponível")
                falhas += 1
        
        return {'enviados': enviados, 'falhas': falhas}
    
    def fechar_navegador(self):
        """Fecha o navegador"""
        if self.driver:
            logger.info("Fechando navegador...")
            self.driver.quit()
            self.driver = None
            self.logged_in = False
    
    def __del__(self):
        """Destrutor - garante que o navegador seja fechado"""
        self.fechar_navegador()


# Instância global para reutilizar a sessão do navegador
_automation_instance = None


def get_automation_instance():
    """Retorna a instância global de automação"""
    global _automation_instance
    if _automation_instance is None:
        _automation_instance = EmailAutomation()
    return _automation_instance


def reset_automation_instance():
    """Reseta a instância de automação (fecha navegador)"""
    global _automation_instance
    if _automation_instance:
        _automation_instance.fechar_navegador()
        _automation_instance = None
