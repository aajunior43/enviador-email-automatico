"""
Script para corrigir o script.js substituindo simulações por chamadas reais à API
"""

import re

# Ler o arquivo original
with open('script.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open('script.js.original', 'w', encoding='utf-8') as f:
    f.write(content)

# Correção 1: Substituir testConnection simulado por chamada real
old_test = r'''    // Simulate connection test
    setTimeout\(\(\) => \{
        showToast\('Conexão OK', 'Credenciais validadas com sucesso', 'success'\);
        updateStatus\('Conectado', 'success'\);
        elements\.testBtn\.disabled = false;
    \}, 2000\);'''

new_test = '''    try {
        showToast('Conectando', 'Abrindo navegador Chrome...', 'info');
        
        const response = await fetch('/api/test-connection', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                url: elements.webmailUrl.value,
                email: elements.emailLogin.value,
                password: elements.emailPassword.value
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Conexão OK', result.message, 'success');
            updateStatus('Conectado', 'success');
        } else {
            showToast('Erro', result.message, 'error');
            updateStatus('Erro', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro', 'Erro: ' + error.message, 'error');
        updateStatus('Erro', 'error');
    } finally {
        elements.testBtn.disabled = false;
    }'''

content = re.sub(old_test, new_test, content, flags=re.MULTILINE)

# Correção 2: Substituir sendSingleEmail simulado por chamada real
old_send = r'''            // Here you would call the Python backend
            console\.log\('Sending email:', data\);

            // Simulate sending
            setTimeout\(\(\) => \{
                showToast\('Sucesso', 'Email enviado com sucesso!', 'success'\);
                updateStatus\('Pronto', 'success'\);

                // Clear form
                elements\.recipient\.value = '';
                elements\.subject\.value = '';
                elements\.message\.value = '';
                elements\.attachment\.value = '';
                elements\.fileList\.innerHTML = '';
                state\.files\.single = \[\];
            \}, 2000\);'''

new_send = '''            try {
                const response = await fetch('/api/send-email', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showToast('Sucesso', result.message, 'success');
                    updateStatus('Pronto', 'success');
                    
                    // Clear form
                    elements.recipient.value = '';
                    elements.subject.value = '';
                    elements.message.value = '';
                    elements.attachment.value = '';
                    elements.fileList.innerHTML = '';
                    state.files.single = [];
                } else {
                    showToast('Erro', result.message, 'error');
                    updateStatus('Erro', 'error');
                }
            } catch (error) {
                console.error('Erro:', error);
                showToast('Erro', 'Erro: ' + error.message, 'error');
                updateStatus('Erro', 'error');
            }'''

content = re.sub(old_send, new_send, content, flags=re.MULTILINE)

# Salvar arquivo corrigido
with open('script.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ script.js corrigido com sucesso!")
print("📝 Backup salvo em: script.js.original")
print("\n🔄 Reinicie o servidor e teste novamente!")
