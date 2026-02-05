# 📧 Enviador de Email Automático - Roundcube

Ferramenta automatizada para enviar emails via Roundcube webmail usando Python e Selenium.

## ✨ Funcionalidades

- 🎨 **Interface Web Moderna** - Interface gráfica elegante e intuitiva (NOVO!)
- 🔐 **Login automático** no Roundcube webmail
- 📧 **Envio único** ou **em lote** (lista de destinatários)
- 📎 **Anexar arquivos** (PDFs, imagens, documentos)
- 🤖 **Detecção de CAPTCHA** com múltiplos métodos
- 📊 **Log completo** de envios com timestamp
- 🔒 **Segurança**: Senha solicitada em tempo de execução (não salva)
- ✅ **Validação de emails** automática

## 🚀 Instalação

### Pré-requisitos
- Python 3.7+
- Google Chrome instalado

### Instalar dependências

```bash
pip install -r requirements.txt
```

## 🔐 Configuração de Credenciais (Opcional)

Para não precisar digitar email e senha toda vez, você pode criar um arquivo `.env`:

1. **Copie o arquivo de exemplo:**
   ```bash
   copy .env.example .env
   ```

2. **Edite o arquivo `.env` e preencha suas credenciais:**
   ```env
   WEBMAIL_URL=https://webmail.instaremail4.com.br/cpsess1913979313/3rdparty/roundcube/?_task=mail&_mbox=INBOX
   EMAIL_LOGIN=seu@email.com
   EMAIL_SENHA=sua_senha_aqui
   ```

3. **Pronto!** O script carregará automaticamente suas credenciais.

> ⚠️ **IMPORTANTE**: O arquivo `.env` está no `.gitignore` e **nunca será enviado ao GitHub** por segurança.

## 📖 Como Usar

### 🎨 Interface Web (Recomendado)

A maneira mais fácil e moderna de usar o enviador de emails!

```bash
cd gui
executar_interface.bat
```

O navegador abrirá automaticamente em `http://localhost:5000` com uma interface moderna e intuitiva.

**Características da Interface Web:**
- ✨ Design moderno dark mode
- 🎯 Interface intuitiva e fácil de usar
- 📱 Responsivo (funciona em qualquer dispositivo)
- 🔔 Notificações em tempo real
- 💾 Salvamento automático de credenciais

📚 **Documentação completa:** [gui/README.md](gui/README.md)

---

### 💻 Linha de Comando (Tradicional)

#### Executar via Batch (Windows)
```bash
executar.bat
```

#### Executar via Python
```bash
python main.py
```

## 📝 Modos de Envio

### 1️⃣ Envio Único
Envia um email para um único destinatário.

**Exemplo de uso:**
```
URL do Webmail: https://webmail.instaremail4.com.br/...
Email de login: seu@email.com
Senha: ********

Escolha uma opção (1-2): 1

Destinatário: destinatario@email.com
Assunto: Teste de envio automático
Mensagem: 
Olá, este é um teste.
Obrigado!
[ENTER]
[ENTER]

Caminho do anexo: C:\documentos\arquivo.pdf
```

### 2️⃣ Envio em Lote
Envia o mesmo email para múltiplos destinatários de uma lista.

**Preparar lista de emails:**
1. Crie um arquivo `.txt` em `destinatarios/`
2. Coloque um email por linha:
```
email1@exemplo.com
email2@exemplo.com
email3@exemplo.com
```

**Exemplo de uso:**
```
Escolha uma opção (1-2): 2

Caminho do arquivo com lista de emails: destinatarios/minha_lista.txt
✅ 15 emails carregados.

Assunto (mesmo para todos): Novidades da Semana
Mensagem:
Olá,
Confira as novidades desta semana!
[ENTER]
[ENTER]

Caminho do anexo: 

⚠️ Você está prestes a enviar 15 emails.
Confirmar envio? (S/N): S
```

### 3️⃣ Envio Automático (Pasta anexos/)
Envia automaticamente emails baseado nos arquivos da pasta `anexos/`.

**Como funciona:**
1. Cada arquivo deve ser nomeado com o email do destinatário
2. O assunto e mensagem são configurados em `config/email_config.env`
3. Cada arquivo é enviado automaticamente para o email correspondente

**Preparar arquivos:**
```
anexos/
├── cliente1@empresa.com.pdf
├── cliente2@empresa.com.pdf
└── cliente3@empresa.com.pdf
```

**Configurar template:**
Edite `config/email_config.env`:
```env
ASSUNTO=Documentos Solicitados
MENSAGEM=Prezado(a),

Segue em anexo os documentos solicitados.

Atenciosamente,
Equipe
```

**Exemplo de uso:**
```
Escolha uma opção (1-3): 3

✅ 15 arquivo(s) encontrado(s) na pasta 'anexos':
   📎 cliente1@empresa.com.pdf
   📎 cliente2@empresa.com.pdf
   ...

📋 Carregando configuração de email...
✅ Assunto: Documentos Solicitados
✅ Mensagem carregada

⚠️ Você está prestes a enviar 15 emails.
Confirmar envio automático? (S/N): S
```

## 📁 Estrutura de Arquivos

```
enviador-email-automatico/
├── main.py                    # Script principal
├── executar.bat               # Atalho de execução
├── README.md                  # Este arquivo
├── requirements.txt           # Dependências
├── config/
│   └── email_template.txt    # Template de email (exemplo)
├── destinatarios/
│   └── lista_exemplo.txt     # Lista de emails (exemplo)
└── logs/
    └── envios_20260127.txt   # Log de envios (gerado automaticamente)
```

## 📊 Log de Envios

Todos os envios são registrados automaticamente em `logs/envios_YYYYMMDD.txt`:

```
[27/01/2026 15:30:45] Para: email1@exemplo.com | Assunto: Teste | Status: SUCESSO
[27/01/2026 15:31:02] Para: email2@exemplo.com | Assunto: Teste | Status: SUCESSO
[27/01/2026 15:31:15] Para: email3@exemplo.com | Assunto: Teste | Status: FALHA
```

## 🤖 Detecção de CAPTCHA

O script detecta CAPTCHAs automaticamente e pausa para resolução manual:

- ✅ Verificação de URL
- ✅ Análise de texto (PT-BR + EN)
- ✅ Detecção de iframes reCAPTCHA

Quando detectado, você resolve manualmente e pressiona ENTER para continuar.

## 🔧 Configurações Avançadas

### Alterar delay entre envios em lote

No arquivo `main.py`, linha ~450:
```python
time.sleep(5)  # Altere para 10, 15, etc. (em segundos)
```

### Personalizar template de email

Edite o arquivo `config/email_template.txt` com seu template padrão.

## ⚠️ Avisos Importantes

### Segurança
- ✅ Senha **nunca** é salva no código
- ✅ Use apenas em redes confiáveis
- ✅ Não compartilhe suas credenciais

### Boas Práticas
- ⏱️ Não envie muitos emails de uma vez (risco de spam)
- 📧 Valide sua lista de destinatários
- 🔍 Sempre teste com envio único primeiro
- 📊 Monitore os logs para verificar falhas

### Limitações
- Funciona especificamente com **Roundcube webmail**
- Requer **Google Chrome** instalado
- Pode precisar de ajustes para versões diferentes do Roundcube

## 🐛 Solução de Problemas

### "Não foi possível localizar campos de login"
- O script tentará permitir login manual
- Faça login manualmente e pressione ENTER

### "Erro ao enviar email"
- Verifique se está logado corretamente
- Confirme que o destinatário é válido
- Verifique sua conexão com a internet

### CAPTCHA aparece frequentemente
- Reduza a frequência de envios
- Use delays maiores entre emails
- Considere usar um IP diferente

## 📄 Licença

MIT License - Sinta-se livre para usar e modificar.

## ⚠️ Aviso Legal

Esta ferramenta é para fins educacionais e de automação pessoal. Use com responsabilidade:
- Não envie spam
- Respeite as políticas do provedor de email
- Obtenha consentimento dos destinatários
- Cumpra a LGPD e outras leis de privacidade
