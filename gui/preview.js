// ===================================
// EMAIL PREVIEW & TEST SEND SYSTEM
// ===================================

class EmailPreview {
    static show(emailData) {
        const modal = document.createElement('div');
        modal.className = 'email-preview-modal';
        
        // Format recipients
        const recipients = Array.isArray(emailData.recipients) ? 
            emailData.recipients.join(', ') : 
            emailData.recipients;
        
        // Format attachments
        const attachmentsHTML = emailData.attachments && emailData.attachments.length > 0 ? `
            <div class="preview-section">
                <h4 class="preview-section-title">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
                    </svg>
                    Anexos
                </h4>
                <div class="preview-attachments">
                    ${emailData.attachments.map(file => `
                        <div class="preview-attachment-item">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                                <polyline points="13 2 13 9 20 9"></polyline>
                            </svg>
                            <span>${file.name || file}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : '';
        
        modal.innerHTML = `
            <div class="email-preview-overlay"></div>
            <div class="email-preview-container">
                <div class="email-preview-header">
                    <h3 class="email-preview-title">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                            <polyline points="22,6 12,13 2,6"></polyline>
                        </svg>
                        Preview do Email
                    </h3>
                    <button class="btn-icon email-preview-close">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
                
                <div class="email-preview-body">
                    <div class="preview-section">
                        <h4 class="preview-section-title">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                                <polyline points="22,6 12,13 2,6"></polyline>
                            </svg>
                            Destinatários
                        </h4>
                        <div class="preview-content">
                            ${recipients}
                        </div>
                    </div>
                    
                    <div class="preview-section">
                        <h4 class="preview-section-title">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="4" y1="9" x2="20" y2="9"></line>
                                <line x1="4" y1="15" x2="20" y2="15"></line>
                                <line x1="10" y1="3" x2="8" y2="21"></line>
                                <line x1="16" y1="3" x2="14" y2="21"></line>
                            </svg>
                            Assunto
                        </h4>
                        <div class="preview-content preview-subject">
                            ${emailData.subject}
                        </div>
                    </div>
                    
                    <div class="preview-section">
                        <h4 class="preview-section-title">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                            </svg>
                            Mensagem
                        </h4>
                        <div class="preview-content preview-message">
                            ${emailData.message.replace(/\n/g, '<br>')}
                        </div>
                    </div>
                    
                    ${attachmentsHTML}
                </div>
                
                <div class="email-preview-footer">
                    <button class="btn btn-secondary" id="closePreviewBtn">Fechar</button>
                    <button class="btn btn-outline" id="testSendBtn">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M22 2L11 13"></path>
                            <path d="M22 2L15 22L11 13L2 9L22 2Z"></path>
                        </svg>
                        Enviar Teste para Mim
                    </button>
                    <button class="btn btn-primary" id="confirmSendBtn">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                        Confirmar e Enviar
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        return new Promise((resolve, reject) => {
            const closeModal = (action) => {
                modal.classList.add('email-preview-closing');
                setTimeout(() => {
                    if (modal.parentElement) {
                        document.body.removeChild(modal);
                    }
                }, 300);
                resolve(action);
            };
            
            // Close button
            modal.querySelector('.email-preview-close').addEventListener('click', () => {
                closeModal('cancel');
            });
            
            modal.querySelector('#closePreviewBtn').addEventListener('click', () => {
                closeModal('cancel');
            });
            
            // Overlay click
            modal.querySelector('.email-preview-overlay').addEventListener('click', () => {
                closeModal('cancel');
            });
            
            // Test send button
            modal.querySelector('#testSendBtn').addEventListener('click', () => {
                closeModal('test');
            });
            
            // Confirm send button
            modal.querySelector('#confirmSendBtn').addEventListener('click', () => {
                closeModal('confirm');
            });
            
            // ESC key
            const escHandler = (e) => {
                if (e.key === 'Escape') {
                    closeModal('cancel');
                    document.removeEventListener('keydown', escHandler);
                }
            };
            document.addEventListener('keydown', escHandler);
        });
    }
    
    static async sendTestEmail(emailData, testRecipient) {
        try {
            const testData = {
                ...emailData,
                recipients: testRecipient,
                subject: '[TESTE] ' + emailData.subject,
                message: '⚠️ ESTE É UM EMAIL DE TESTE ⚠️\n\n' + emailData.message
            };
            
            const response = await fetch('/api/send-test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(testData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                window.toastManager.success('Email de teste enviado com sucesso!');
                return true;
            } else {
                window.toastManager.error('Erro ao enviar email de teste: ' + result.error);
                return false;
            }
        } catch (error) {
            console.error('Erro ao enviar email de teste:', error);
            window.toastManager.error('Erro ao enviar email de teste');
            return false;
        }
    }
}

// Helper function to gather email data from current form
function gatherEmailData() {
    const mode = state.currentMode;
    let emailData = {
        mode: mode,
        recipients: '',
        subject: '',
        message: '',
        attachments: []
    };
    
    switch (mode) {
        case 'single':
            emailData.recipients = document.getElementById('recipient')?.value || '';
            emailData.subject = document.getElementById('subject')?.value || '';
            emailData.message = document.getElementById('message')?.value || '';
            emailData.attachments = state.files.single || [];
            break;
            
        case 'batch':
            const recipientList = document.getElementById('recipientList')?.value || '';
            emailData.recipients = recipientList.split(/[,;\n]/).map(e => e.trim()).filter(e => e);
            emailData.subject = document.getElementById('batchSubject')?.value || '';
            emailData.message = document.getElementById('batchMessage')?.value || '';
            emailData.attachments = state.files.batch || [];
            break;
            
        case 'auto':
            emailData.recipients = 'Baseado em arquivos';
            emailData.subject = document.getElementById('autoSubject')?.value || '';
            emailData.message = document.getElementById('autoMessage')?.value || '';
            emailData.attachments = ['Arquivos da pasta anexos/'];
            break;
    }
    
    return emailData;
}

// Add preview button handlers
function setupPreviewHandlers() {
    const previewButtons = document.querySelectorAll('[data-action="preview"]');
    
    previewButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
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
                    await EmailPreview.sendTestEmail(emailData, testEmail);
                }
            } else if (action === 'confirm') {
                // Trigger the actual send
                const sendBtn = document.querySelector('[data-action="send"]');
                if (sendBtn) {
                    sendBtn.click();
                }
            }
        });
    });
}

window.EmailPreview = EmailPreview;
window.gatherEmailData = gatherEmailData;
window.setupPreviewHandlers = setupPreviewHandlers;
