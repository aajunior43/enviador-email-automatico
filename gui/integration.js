// ===================================
// INTEGRATION & ENHANCEMENTS
// ===================================

// Override old showToast with new ToastManager
window.showToast = function(title, message, type = 'success') {
    window.toastManager.show(message || title, type);
};

// Initialize validators on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeValidators();
    initializeProgressTracking();
    enhanceSendButtons();
    setupPreviewHandlers();
    initializeTemplates();
    enhanceModeSelection();
});

function initializeValidators() {
    // Email validators for single mode
    const recipientInput = document.getElementById('recipient');
    if (recipientInput) {
        new EmailValidator(recipientInput, {
            showIcon: true,
            showMessage: true,
            validateOnType: true
        });
    }
    
    // Email login validator
    const emailLoginInput = document.getElementById('emailLogin');
    if (emailLoginInput) {
        new EmailValidator(emailLoginInput, {
            showIcon: true,
            showMessage: false,
            validateOnType: false
        });
    }
    
    // Password strength indicator
    const passwordInput = document.getElementById('emailPassword');
    if (passwordInput) {
        new PasswordStrengthIndicator(passwordInput, {
            showBar: true,
            showLabel: true,
            showFeedback: false
        });
    }
    
    // Batch mode - validate on blur
    const recipientListInput = document.getElementById('recipientList');
    if (recipientListInput) {
        recipientListInput.addEventListener('blur', () => {
            const text = recipientListInput.value;
            if (text.trim()) {
                const result = Validator.validateEmailList(text);
                if (result.invalid.length > 0) {
                    window.toastManager.warning(
                        `${result.invalid.length} email(s) inválido(s) encontrado(s): ${result.invalid.slice(0, 3).join(', ')}...`
                    );
                }
            }
        });
    }
}

function initializeProgressTracking() {
    // Store original send functions
    if (typeof window.originalSendBatchEmails === 'undefined' && typeof sendBatchEmails !== 'undefined') {
        window.originalSendBatchEmails = sendBatchEmails;
        
        // Override sendBatchEmails to add progress bar
        window.sendBatchEmails = async function(emails) {
            // Check for mass action confirmation
            const confirmed = await confirmMassAction(emails.length, 'enviar');
            if (!confirmed) {
                window.toastManager.info('Envio cancelado pelo usuário');
                return;
            }
            
            // Create progress container
            const logContainer = document.getElementById('logContainer');
            if (logContainer) {
                const progressContainer = document.createElement('div');
                progressContainer.id = 'batch-progress-container';
                logContainer.insertBefore(progressContainer, logContainer.firstChild);
                
                const progressBar = new ProgressBar(progressContainer, {
                    showPercentage: true,
                    showCounter: true,
                    showTime: true
                });
                
                progressBar.start(emails.length);
                
                // Track progress
                let completed = 0;
                const originalAddLog = window.addLog;
                window.addLog = function(message, type) {
                    originalAddLog(message, type);
                    
                    if (type === 'success' && message.includes('✅')) {
                        completed++;
                        progressBar.update(completed, `Enviando email ${completed} de ${emails.length}...`);
                    } else if (type === 'error' && message.includes('❌')) {
                        completed++;
                        progressBar.update(completed, `Email ${completed} falhou`);
                    }
                    
                    if (completed === emails.length) {
                        progressBar.complete(`${completed} emails processados!`);
                        window.addLog = originalAddLog;
                        
                        setTimeout(() => {
                            progressBar.destroy();
                        }, 5000);
                    }
                };
            }
            
            // Call original function
            return window.originalSendBatchEmails(emails);
        };
    }
}

function enhanceSendButtons() {
    // Add preview functionality to the existing preview button
    const previewBtn = document.getElementById('previewBtn');
    if (previewBtn) {
        previewBtn.removeEventListener('click', previewBtn.onclick);
        previewBtn.onclick = null;
        
        previewBtn.addEventListener('click', async () => {
            try {
                const emailData = gatherEmailData();
                
                // Validate
                if (!emailData.recipients || (Array.isArray(emailData.recipients) && emailData.recipients.length === 0)) {
                    window.toastManager.warning('Adicione pelo menos um destinatário');
                    return;
                }
                
                if (!emailData.subject) {
                    window.toastManager.warning('Digite um assunto para o email');
                    return;
                }
                
                if (!emailData.message) {
                    window.toastManager.warning('Digite uma mensagem para o email');
                    return;
                }
                
                // Show preview
                const action = await EmailPreview.show(emailData);
                
                if (action === 'test') {
                    // Prompt for test email
                    const testEmail = prompt('Digite o email para envio de teste:', state.credentials.email);
                    if (testEmail && Validator.isValidEmail(testEmail)) {
                        const testData = {
                            ...emailData,
                            recipients: testEmail,
                            mode: 'single'
                        };
                        await sendTestEmail(testData);
                    } else if (testEmail) {
                        window.toastManager.error('Email inválido');
                    }
                } else if (action === 'confirm') {
                    // Trigger the actual send
                    const sendBtn = document.getElementById('sendBtn');
                    if (sendBtn) {
                        sendBtn.click();
                    }
                }
            } catch (error) {
                console.error('Erro no preview:', error);
                window.toastManager.error('Erro ao gerar preview');
            }
        });
    }
}

async function sendTestEmail(emailData) {
    try {
        updateStatus('Enviando teste...', 'info');
        addLog('📧 Enviando email de teste...', 'info');
        
        const response = await fetch('/api/send-email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mode: 'single',
                credentials: {
                    url: document.getElementById('webmailUrl').value,
                    email: document.getElementById('emailLogin').value,
                    password: document.getElementById('emailPassword').value
                },
                recipient: emailData.recipients,
                subject: '[TESTE] ' + emailData.subject,
                message: '⚠️ ESTE É UM EMAIL DE TESTE ⚠️\n\n' + emailData.message,
                files: emailData.attachments || []
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            addLog('✅ Email de teste enviado com sucesso!', 'success');
            window.toastManager.success('Email de teste enviado!');
            updateStatus('Pronto', 'success');
        } else {
            addLog('❌ Erro ao enviar teste: ' + result.message, 'error');
            window.toastManager.error('Erro ao enviar teste: ' + result.message);
            updateStatus('Erro', 'error');
        }
    } catch (error) {
        console.error('Erro ao enviar email de teste:', error);
        addLog('❌ Erro: ' + error.message, 'error');
        window.toastManager.error('Erro ao enviar email de teste');
        updateStatus('Erro', 'error');
    }
}

// Replace all alert() calls with toasts
window.alert = function(message) {
    window.toastManager.info(message, 8000);
};

// Enhance confirm dialogs for better UX
const originalConfirm = window.confirm;
window.confirm = function(message) {
    // For mass actions, use our custom modal
    if (message.includes('enviar') || message.includes('email')) {
        return confirmMassAction(1, 'confirmar');
    }
    return originalConfirm(message);
};

function initializeTemplates() {
    const container = document.getElementById('templatesContainer');
    if (container) {
        window.templateUI = new TemplateUI(container, window.templateManager);
    }
}

function enhanceModeSelection() {
    // Add templates to mode options
    const modeTemplates = document.getElementById('modeTemplates');
    if (modeTemplates) {
        modeTemplates.addEventListener('click', () => {
            // Hide all other sections
            document.querySelectorAll('.email-form-card').forEach(section => {
                section.classList.add('hidden');
            });
            
            // Show templates section
            const templatesSection = document.getElementById('templatesSection');
            if (templatesSection) {
                templatesSection.classList.remove('hidden');
            }
            
            // Update mode buttons
            document.querySelectorAll('.mode-option').forEach(btn => {
                btn.classList.remove('active');
            });
            modeTemplates.classList.add('active');
            
            state.currentMode = 'templates';
        });
    }
}

console.log('✅ Componentes de melhorias carregados com sucesso!');
