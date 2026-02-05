# 🎨 Interface Web Moderna - Enviador de Email Automático

Interface visual moderna e elegante para o enviador de email automático via Roundcube.

## ✨ Características

- 🌙 **Design Dark Mode Premium** - Interface moderna com gradientes vibrantes
- 🎯 **Interface Intuitiva** - Navegação simples e clara
- 📱 **Responsivo** - Funciona em desktop, tablet e mobile
- ⚡ **Rápido e Fluido** - Animações suaves e transições elegantes
- 🔔 **Notificações Toast** - Feedback visual em tempo real
- 💾 **Salvamento Automático** - Credenciais salvas localmente (exceto senha)

## 🚀 Como Usar

### 🔐 Credenciais Compartilhadas com CLI

A interface web **carrega automaticamente** as credenciais do arquivo `.env` (mesmo arquivo usado pelo script CLI), garantindo consistência entre as duas interfaces!

**Como funciona:**
1. Configure o arquivo `.env` na raiz do projeto:
   ```env
   WEBMAIL_URL=https://webmail.instaremail4.com.br/...
   EMAIL_LOGIN=seu@email.com
   EMAIL_SENHA=sua_senha_aqui
   ```

2. Ao abrir a interface web, as credenciais serão **carregadas automaticamente**
3. Se houver senha configurada no `.env`, você verá uma indicação visual ✅
4. As mesmas credenciais funcionam tanto na CLI quanto na interface web

### Método 1: Executar via Batch (Recomendado)

1. **Execute o arquivo:**
   ```
   executar_interface.bat
   ```

2. **O navegador abrirá automaticamente** em `http://localhost:5000`

### Método 2: Executar via Python

1. **Instale as dependências:**
   ```bash
   pip install flask flask-cors
   ```

2. **Execute o servidor:**
   ```bash
   cd gui
   python server.py
   ```

3. **Abra o navegador** em `http://localhost:5000`

## 📖 Funcionalidades

### 🔐 Credenciais de Acesso
- Configure URL do webmail, email e senha
- Credenciais salvas localmente (exceto senha por segurança)
- Botão de teste de conexão

### 📧 Modos de Envio

#### 1️⃣ Envio Único
- Envie para um destinatário específico
- Campos: destinatário, assunto, mensagem
- Suporte a múltiplos anexos
- Validação de email em tempo real

#### 2️⃣ Envio em Lote
- Envie para múltiplos destinatários
- Digite um email por linha
- Contador de emails válidos em tempo real
- Mesmo assunto e mensagem para todos
- Anexos opcionais

#### 3️⃣ Envio Automático
- Baseado em arquivos na pasta `anexos/`
- Nomeie arquivos com o email do destinatário
- Exemplo: `cliente@empresa.com.pdf`
- Configure assunto e mensagem padrão

## 🎨 Design

### Paleta de Cores
- **Primária:** Roxo vibrante (#6366F1)
- **Fundo:** Dark mode premium
- **Acentos:** Gradientes suaves
- **Texto:** Alta legibilidade

### Tipografia
- **Fonte:** Inter (Google Fonts)
- **Pesos:** 300-800
- **Hierarquia clara** e legível

### Animações
- Transições suaves (250ms)
- Micro-animações nos botões
- Feedback visual em todas as ações
- Efeitos hover elegantes

## 🔧 Estrutura de Arquivos

```
gui/
├── index.html              # Estrutura HTML
├── styles.css              # Estilos CSS modernos
├── script.js               # Lógica JavaScript
├── server.py               # Servidor Flask (backend)
├── executar_interface.bat  # Atalho de execução
└── README.md              # Este arquivo
```

## 🌐 API Endpoints

O servidor Flask fornece os seguintes endpoints:

### `POST /api/test-connection`
Testa a conexão com o webmail
```json
{
  "url": "https://webmail.exemplo.com",
  "email": "seu@email.com",
  "password": "senha"
}
```

### `POST /api/send-email`
Envia email(s) baseado no modo
```json
{
  "mode": "single|batch|auto",
  "credentials": {...},
  "recipient": "...",
  "subject": "...",
  "message": "..."
}
```

### `GET /api/logs`
Retorna logs de envio
```
GET /api/logs?date=20260205
```

### `GET /api/files`
Lista arquivos na pasta anexos
```
GET /api/files
```

## 💡 Dicas de Uso

1. **Teste primeiro** - Use "Testar Conexão" antes de enviar
2. **Envio único** - Sempre teste com envio único primeiro
3. **Validação** - A interface valida emails em tempo real
4. **Logs** - Clique em "Ver Logs" para acompanhar envios
5. **Ajuda** - Clique em "Ajuda" para instruções detalhadas

## 🔒 Segurança

- ✅ Senha **nunca** é salva no navegador
- ✅ Comunicação via localhost
- ✅ Validação de dados no frontend e backend
- ✅ Logs detalhados de todas as operações

## 🐛 Solução de Problemas

### Porta 5000 já em uso
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Flask não encontrado
```bash
pip install flask flask-cors
```

### Navegador não abre automaticamente
Abra manualmente: `http://localhost:5000`

## 📄 Licença

MIT License - Mesma do projeto principal

## 🎯 Próximas Melhorias

- [ ] Upload de arquivos via interface
- [ ] Editor de templates de email
- [ ] Agendamento de envios
- [ ] Dashboard com estatísticas
- [ ] Temas personalizáveis
- [ ] Exportação de relatórios

## 💬 Suporte

Para dúvidas ou problemas, consulte o README principal do projeto.

---

**Desenvolvido com ❤️ usando HTML, CSS, JavaScript e Flask**
