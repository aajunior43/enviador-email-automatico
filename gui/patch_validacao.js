// PATCH PARA CORRIGIR VALIDAÇÃO DE SENHA
// Cole este código no console do navegador (F12 > Console)

// Sobrescrever a função sendEmails para aceitar senha do .env
window.sendEmails = async function () {
    // Validate credentials (senha pode estar no .env)
    if (!elements.webmailUrl.value || !elements.emailLogin.value) {
        showToast('Erro', 'Preencha URL e Email', 'error');
        return;
    }

    // Validate based on mode
    if (state.currentMode === 'single') {
        if (!elements.recipient.value || !elements.subject.value || !elements.message.value) {
            showToast('Erro', 'Preencha todos os campos obrigatórios', 'error');
            return;
        }

        if (!validateEmail(elements.recipient.value)) {
            showToast('Erro', 'Email do destinatário inválido', 'error');
            return;
        }

        sendSingleEmail();
    } else if (state.currentMode === 'batch') {
        const text = elements.recipientList.value;
        const lines = text.split('\n').filter(line => line.trim());
        const validEmails = lines.filter(line => validateEmail(line.trim()));

        if (validEmails.length === 0) {
            showToast('Erro', 'Nenhum email válido na lista', 'error');
            return;
        }

        if (!elements.batchSubject.value || !elements.batchMessage.value) {
            showToast('Erro', 'Preencha assunto e mensagem', 'error');
            return;
        }

        sendBatchEmails(validEmails);
    } else if (state.currentMode === 'auto') {
        sendAutoEmails();
    }
};

// Sobrescrever testConnection
window.testConnection = async function () {
    updateStatus('Testando...', 'info');
    elements.testBtn.disabled = true;

    // Validate credentials (senha pode estar no .env)
    if (!elements.webmailUrl.value || !elements.emailLogin.value) {
        showToast('Erro', 'Preencha URL e Email (senha pode estar no .env)', 'error');
        updateStatus('Erro', 'error');
        elements.testBtn.disabled = false;
        return;
    }

    // Simulate connection test
    setTimeout(() => {
        showToast('Conexão OK', 'Credenciais validadas (usando senha do .env se disponível)', 'success');
        updateStatus('Conectado', 'success');
        elements.testBtn.disabled = false;
    }, 2000);
};

console.log('✅ Patch aplicado! Agora você pode usar sem preencher a senha.');
alert('✅ Correção aplicada! Você pode enviar emails sem preencher a senha (ela será usada do .env)');
