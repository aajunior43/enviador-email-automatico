// Adicione este código no console do navegador para testar o carregamento:

fetch('/api/credentials')
    .then(response => response.json())
    .then(data => {
        console.log('Credenciais do .env:', data);
        if (data.success && data.credentials) {
            document.getElementById('webmailUrl').value = data.credentials.url || '';
            document.getElementById('emailLogin').value = data.credentials.email || '';
            if (data.credentials.hasPassword) {
                document.getElementById('emailPassword').placeholder = '••••••••  (configurada no .env)';
                document.getElementById('emailPassword').style.borderColor = 'var(--color-success)';
                alert('✅ Credenciais carregadas do .env com sucesso!');
            }
        }
    })
    .catch(error => console.error('Erro:', error));
