// PATCH - Cole este código no console do navegador (F12 > Console) para corrigir o envio

// Sobrescrever função sendSingleEmail para fazer chamada real à API
window.sendSingleEmail = async function () {
    const data = {
        mode: 'single',
        credentials: {
            url: elements.webmailUrl.value,
            email: elements.emailLogin.value,
            password: elements.emailPassword.value
        },
        recipient: elements.recipient.value,
        subject: elements.subject.value,
        message: elements.message.value,
        files: state.files.single
    };

    showModal(
        'Confirmar Envio',
        `
            <p>Você está prestes a enviar um email para:</p>
            <p style="margin-top: 1rem;"><strong>${data.recipient}</strong></p>
            <p style="margin-top: 1rem; color: var(--color-text-secondary);">Assunto: ${data.subject}</p>
            <p style="margin-top: 0.5rem; color: #f59e0b;">⚠️ O navegador Chrome será aberto para envio real!</p>
        `,
        async () => {
            updateStatus('Enviando...', 'info');
            showToast('Enviando', 'Abrindo navegador e enviando email...', 'info');

            try {
                // Chamar API real do backend
                const response = await fetch('/api/send-email', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (result.success) {
                    showToast('Sucesso', result.message || 'Email enviado com sucesso!', 'success');
                    updateStatus('Pronto', 'success');

                    // Clear form
                    elements.recipient.value = '';
                    elements.subject.value = '';
                    elements.message.value = '';
                    elements.attachment.value = '';
                    elements.fileList.innerHTML = '';
                    state.files.single = [];
                } else {
                    showToast('Erro', result.message || 'Falha ao enviar email', 'error');
                    updateStatus('Erro', 'error');
                }
            } catch (error) {
                console.error('Erro ao enviar email:', error);
                showToast('Erro', 'Erro ao comunicar com o servidor: ' + error.message, 'error');
                updateStatus('Erro', 'error');
            }
        }
    );
};

// Sobrescrever testConnection também
window.testConnection = async function () {
    updateStatus('Testando...', 'info');
    elements.testBtn.disabled = true;

    if (!elements.webmailUrl.value || !elements.emailLogin.value) {
        showToast('Erro', 'Preencha URL e Email (senha pode estar no .env)', 'error');
        updateStatus('Erro', 'error');
        elements.testBtn.disabled = false;
        return;
    }

    try {
        showToast('Conectando', 'Abrindo navegador Chrome...', 'info');

        const response = await fetch('/api/test-connection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
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
        console.error('Erro ao testar conexão:', error);
        showToast('Erro', 'Erro ao comunicar com o servidor: ' + error.message, 'error');
        updateStatus('Erro', 'error');
    } finally {
        elements.testBtn.disabled = false;
    }
};

console.log('✅ Patch aplicado! Agora as funções fazem chamadas reais à API.');
alert('✅ Correção aplicada! Agora o envio é REAL via Selenium.\n\n1. Clique em "Testar Conexão" primeiro\n2. Aguarde o Chrome abrir\n3. Depois envie emails normalmente');
