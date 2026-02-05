# 🔧 SOLUÇÃO RÁPIDA - Credenciais não carregam

## Problema
As credenciais do .env não estão sendo carregadas automaticamente na interface web.

## Solução Imediata

### Opção 1: Teste no Console do Navegador

1. **Abra a interface web** (`executar_interface.bat`)
2. **Pressione F12** para abrir o DevTools
3. **Vá na aba Console**
4. **Cole e execute este código:**

```javascript
fetch('/api/credentials')
    .then(response => response.json())
    .then(data => {
        console.log('Resposta da API:', data);
        if (data.success && data.credentials) {
            document.getElementById('webmailUrl').value = data.credentials.url || '';
            document.getElementById('emailLogin').value = data.credentials.email || '';
            if (data.credentials.hasPassword) {
                document.getElementById('emailPassword').placeholder = '••••••••  (configurada no .env)';
                document.getElementById('emailPassword').style.borderColor = '#10b981';
                alert('✅ Credenciais carregadas com sucesso!');
            }
        }
    })
    .catch(error => console.error('Erro:', error));
```

### Opção 2: Recarregar a Página

1. **Feche o navegador completamente**
2. **Pare o servidor** (Ctrl+C no terminal)
3. **Execute novamente:** `executar_interface.bat`
4. **Aguarde 2-3 segundos** antes de interagir

### Opção 3: Preencher Manualmente (Temporário)

Enquanto corrigimos, você pode preencher manualmente:
- **URL**: https://webmail.instaremail4.com.br/cpsess1913979313/3rdparty/roundcube/?_task=mail&_mbox=INBOX
- **Email**: tesouraria@inaja.pr.gov.br
- **Senha**: (a senha do .env)

## Verificar se o Servidor Está Funcionando

No terminal onde o servidor está rodando, você deve ver:
```
🌐 Servidor iniciando em: http://localhost:5000
```

Se não ver isso, o servidor não iniciou corretamente.

## Testar API Diretamente

Abra no navegador:
```
http://localhost:5000/api/credentials
```

Você deve ver algo como:
```json
{
  "success": true,
  "credentials": {
    "url": "https://webmail.instaremail4.com.br/...",
    "email": "tesouraria@inaja.pr.gov.br",
    "hasPassword": true
  }
}
```

## Se Nada Funcionar

1. **Verifique o .env:**
   ```bash
   type ..\..env
   ```

2. **Reinstale dependências:**
   ```bash
   pip install --upgrade flask flask-cors python-dotenv
   ```

3. **Use a interface CLI temporariamente:**
   ```bash
   cd ..
   python main.py
   ```
