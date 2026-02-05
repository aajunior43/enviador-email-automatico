// ===================================
// STATE MANAGEMENT
// ===================================
const state = {
    currentMode: 'single',
    credentials: {
        url: '',
        email: '',
        password: ''
    },
    files: {
        single: [],
        batch: []
    },
    selectedTriagemFiles: new Set()
};

// ===================================
// DOM ELEMENTS
// ===================================
const elements = {
    // Mode buttons
    modeSingle: document.getElementById('modeSingle'),
    modeBatch: document.getElementById('modeBatch'),
    modeAuto: document.getElementById('modeAuto'),
    modeOrganizer: document.getElementById('modeOrganizer'),
    modeContacts: document.getElementById('modeContacts'),

    // Forms
    singleModeForm: document.getElementById('singleModeForm'),
    batchModeForm: document.getElementById('batchModeForm'),
    batchModeForm: document.getElementById('batchModeForm'),
    autoModeForm: document.getElementById('autoModeForm'),
    organizerSection: document.getElementById('organizerSection'),
    contactsSection: document.getElementById('contactsSection'),

    // Inputs
    webmailUrl: document.getElementById('webmailUrl'),
    emailLogin: document.getElementById('emailLogin'),
    emailPassword: document.getElementById('emailPassword'),
    togglePassword: document.getElementById('togglePassword'),

    // Single mode
    recipient: document.getElementById('recipient'),
    subject: document.getElementById('subject'),
    message: document.getElementById('message'),
    attachment: document.getElementById('attachment'),
    fileList: document.getElementById('fileList'),

    // Batch mode
    recipientList: document.getElementById('recipientList'),
    emailCount: document.getElementById('emailCount'),
    batchSubject: document.getElementById('batchSubject'),
    batchMessage: document.getElementById('batchMessage'),
    batchAttachment: document.getElementById('batchAttachment'),
    batchFileList: document.getElementById('batchFileList'),

    // Auto mode
    autoSubject: document.getElementById('autoSubject'),
    autoMessage: document.getElementById('autoMessage'),

    // Buttons
    testBtn: document.getElementById('testBtn'),
    previewBtn: document.getElementById('previewBtn'),
    sendBtn: document.getElementById('sendBtn'),

    // Status
    statusBadge: document.getElementById('statusBadge'),

    // Toast
    toastContainer: document.getElementById('toastContainer'),

    // Modal
    modal: document.getElementById('modal'),
    modalOverlay: document.getElementById('modalOverlay'),
    modalClose: document.getElementById('modalClose'),
    modalTitle: document.getElementById('modalTitle'),
    modalBody: document.getElementById('modalBody'),
    modalFooter: document.getElementById('modalFooter'),
    modalCancel: document.getElementById('modalCancel'),
    modalConfirm: document.getElementById('modalConfirm'),

    // Links
    viewLogsLink: document.getElementById('viewLogsLink'),
    helpLink: document.getElementById('helpLink'),

    // Log
    logContainer: document.getElementById('logContainer'),
    clearLogBtn: document.getElementById('clearLogBtn'),

    // Organizer
    triagemList: document.getElementById('triagemList'),
    filePreview: document.getElementById('filePreview'),
    organizerEmail: document.getElementById('organizerEmail'),
    organizerControls: document.getElementById('organizerControls'),
    refreshTriagemBtn: document.getElementById('refreshTriagemBtn'),
    processFileBtn: document.getElementById('processFileBtn'),
    scanEmailBtn: document.getElementById('scanEmailBtn'),

    // Contacts
    contactsTable: document.getElementById('contactsTable'),
    noContactsMessage: document.getElementById('noContactsMessage')
};

// ===================================
// INITIALIZATION
// ===================================
async function init() {
    setupEventListeners();
    await loadCredentialsFromEnv();  // Aguardar carregamento do .env
    updateStatus('Pronto', 'success');

    // Add smooth entrance animation
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.5s ease';
        document.body.style.opacity = '1';
    }, 100);
}

// ===================================
// EVENT LISTENERS
// ===================================
function setupEventListeners() {
    // Mode selection
    elements.modeSingle.addEventListener('click', () => switchMode('single'));
    elements.modeBatch.addEventListener('click', () => switchMode('batch'));
    elements.modeAuto.addEventListener('click', () => switchMode('auto'));
    elements.modeOrganizer.addEventListener('click', () => switchMode('organizer'));
    if (elements.modeContacts) elements.modeContacts.addEventListener('click', () => switchMode('contacts'));

    // Password toggle
    elements.togglePassword.addEventListener('click', togglePasswordVisibility);

    // File inputs
    elements.attachment.addEventListener('change', (e) => handleFileSelect(e, 'single'));
    elements.batchAttachment.addEventListener('change', (e) => handleFileSelect(e, 'batch'));

    // Recipient list validation
    elements.recipientList.addEventListener('input', validateRecipientList);

    // Buttons
    elements.testBtn.addEventListener('click', testConnection);
    elements.previewBtn.addEventListener('click', showPreview);
    elements.sendBtn.addEventListener('click', sendEmails);

    // Modal
    elements.modalOverlay.addEventListener('click', closeModal);
    elements.modalClose.addEventListener('click', closeModal);
    elements.modalCancel.addEventListener('click', closeModal);

    // Links
    elements.viewLogsLink.addEventListener('click', (e) => {
        e.preventDefault();
        viewLogs();
    });

    elements.helpLink.addEventListener('click', (e) => {
        e.preventDefault();
        showHelp();
    });

    // Save credentials on change
    elements.webmailUrl.addEventListener('change', saveCredentials);
    elements.emailLogin.addEventListener('change', saveCredentials);
    elements.emailPassword.addEventListener('change', saveCredentials);

    // Clear log button
    if (elements.clearLogBtn) {
        elements.clearLogBtn.addEventListener('click', clearLog);
    }

    // Organizer Listeners
    if (elements.refreshTriagemBtn) elements.refreshTriagemBtn.addEventListener('click', loadTriagemFiles);
    if (elements.processFileBtn) elements.processFileBtn.addEventListener('click', processTriagemFile);
    if (elements.scanEmailBtn) elements.scanEmailBtn.addEventListener('click', scanEmail);
}

// ===================================
// LOG MANAGEMENT
// ===================================
const logIcons = {
    info: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><path d="M12 16V12M12 8H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`,
    success: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    warning: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 9V13M12 17H12.01M10.29 3.86L1.82 18C1.64 18.3 1.59 18.66 1.67 18.99C1.75 19.32 1.97 19.59 2.27 19.77C2.57 19.95 2.93 20.02 3.28 19.97C3.63 19.92 3.95 19.76 4.18 19.5L12 9L19.82 19.5C20.05 19.76 20.37 19.92 20.72 19.97C21.07 20.02 21.43 19.95 21.73 19.77C22.03 19.59 22.25 19.32 22.33 18.99C22.41 18.66 22.36 18.3 22.18 18L13.71 3.86C13.53 3.56 13.27 3.32 12.96 3.17C12.65 3.02 12.3 2.97 11.96 3.02C11.62 3.07 11.3 3.22 11.06 3.45C10.82 3.68 10.66 3.98 10.61 4.31" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    error: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    step: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M9 5L16 12L9 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`
};

function addLog(message, type = 'info') {
    const container = elements.logContainer;

    // Remove empty state if present
    const emptyState = container.querySelector('.log-empty');
    if (emptyState) {
        emptyState.remove();
    }

    // Create log entry
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;

    const time = new Date().toLocaleTimeString('pt-BR');

    entry.innerHTML = `
        <span class="log-time">[${time}]</span>
        <span class="log-icon">${logIcons[type] || logIcons.info}</span>
        <span class="log-message">${message}</span>
    `;

    container.appendChild(entry);

    // Auto scroll to bottom
    container.scrollTop = container.scrollHeight;
}

function clearLog() {
    elements.logContainer.innerHTML = `
        <div class="log-empty">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 5H7C5.89543 5 5 5.89543 5 7V19C5 20.1046 5.89543 21 7 21H17C18.1046 21 19 20.1046 19 19V7C19 5.89543 18.1046 5 17 5H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <p>Log limpo. Clique em "Testar Conexão" para começar.</p>
        </div>
    `;
}

// ===================================
// MODE SWITCHING
// ===================================
function switchMode(mode) {
    state.currentMode = mode;

    // Update button states
    elements.modeSingle.classList.toggle('active', mode === 'single');
    elements.modeBatch.classList.toggle('active', mode === 'batch');
    elements.modeAuto.classList.toggle('active', mode === 'auto');
    elements.modeOrganizer.classList.toggle('active', mode === 'organizer');
    if (elements.modeContacts) elements.modeContacts.classList.toggle('active', mode === 'contacts');

    elements.singleModeForm.classList.toggle('hidden', mode !== 'single');
    elements.batchModeForm.classList.toggle('hidden', mode !== 'batch');
    elements.autoModeForm.classList.toggle('hidden', mode !== 'auto');

    if (elements.organizerSection) {
        elements.organizerSection.classList.toggle('hidden', mode !== 'organizer');
    }
    if (elements.contactsSection) {
        elements.contactsSection.classList.toggle('hidden', mode !== 'contacts');
    }

    // Gerenciar visibilidade dos botões principais
    const actionButtons = document.querySelector('.action-buttons');
    if (mode === 'organizer') {
        if (actionButtons) actionButtons.classList.add('hidden');
        loadTriagemFiles();
    } else if (mode === 'contacts') {
        if (actionButtons) actionButtons.classList.add('hidden');
        loadContacts();
    } else {
        if (actionButtons) actionButtons.classList.remove('hidden');
    }

    // Smooth scroll to form
    setTimeout(() => {
        const activeForm = document.querySelector('.email-form-card:not(.hidden)');
        if (activeForm) {
            activeForm.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }, 100);
}

// ===================================
// PASSWORD VISIBILITY
// ===================================
function togglePasswordVisibility() {
    const input = elements.emailPassword;
    const icon = elements.togglePassword.querySelector('svg');

    if (input.type === 'password') {
        input.type = 'text';
        icon.innerHTML = `
            <path d="M17.94 17.94C16.2306 19.243 14.1491 19.9649 12 20C5 20 1 12 1 12C2.24389 9.68192 3.96914 7.65663 6.06 6.06M9.9 4.24C10.5883 4.0789 11.2931 3.99836 12 4C19 4 23 12 23 12C22.393 13.1356 21.6691 14.2048 20.84 15.19M14.12 14.12C13.8454 14.4148 13.5141 14.6512 13.1462 14.8151C12.7782 14.9791 12.3809 15.0673 11.9781 15.0744C11.5753 15.0815 11.1752 15.0074 10.8016 14.8565C10.4281 14.7056 10.0887 14.4811 9.80385 14.1962C9.51897 13.9113 9.29439 13.5719 9.14351 13.1984C8.99262 12.8248 8.91853 12.4247 8.92563 12.0219C8.93274 11.6191 9.02091 11.2218 9.18488 10.8538C9.34884 10.4858 9.58525 10.1546 9.88 9.88" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M1 1L23 23" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        `;
    } else {
        input.type = 'password';
        icon.innerHTML = `
            <path d="M2.45825 12C3.73253 7.94288 7.52281 5 12.0004 5C16.4781 5 20.2684 7.94291 21.5426 12C20.2684 16.0571 16.4781 19 12.0005 19C7.52281 19 3.73251 16.0571 2.45825 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        `;
    }
}

// ===================================
// FILE HANDLING
// ===================================
function handleFileSelect(event, mode) {
    const files = Array.from(event.target.files);
    state.files[mode] = files;

    const fileListElement = mode === 'single' ? elements.fileList : elements.batchFileList;
    fileListElement.innerHTML = '';

    files.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <div class="file-item-name">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 16px; height: 16px; color: var(--color-primary);">
                    <path d="M15.172 7L20.414 12.242C21.195 13.023 21.195 14.291 20.414 15.072L15.072 20.414C14.291 21.195 13.023 21.195 12.242 20.414L3.51472 11.6868C2.73367 10.9057 2.73367 9.63769 3.51472 8.85664L8.85786 3.51351C9.63891 2.73246 10.9069 2.73246 11.688 3.51351L15.172 7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>${file.name}</span>
                <span style="color: var(--color-text-tertiary); font-size: 0.75rem;">(${formatFileSize(file.size)})</span>
            </div>
            <button class="file-item-remove" onclick="removeFile(${index}, '${mode}')">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 16px; height: 16px;">
                    <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
        `;
        fileListElement.appendChild(fileItem);
    });
}

function removeFile(index, mode) {
    state.files[mode].splice(index, 1);

    // Update file input
    const input = mode === 'single' ? elements.attachment : elements.batchAttachment;
    const dt = new DataTransfer();
    state.files[mode].forEach(file => dt.items.add(file));
    input.files = dt.files;

    // Trigger change event to update UI
    input.dispatchEvent(new Event('change'));
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// ===================================
// EMAIL VALIDATION
// ===================================
function validateEmail(email) {
    const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return re.test(email);
}

function validateRecipientList() {
    const text = elements.recipientList.value;
    const lines = text.split('\n').filter(line => line.trim());
    const validEmails = lines.filter(line => validateEmail(line.trim()));

    elements.emailCount.textContent = `${validEmails.length} emails válidos`;

    if (validEmails.length > 0) {
        elements.emailCount.style.color = 'var(--color-success)';
    } else {
        elements.emailCount.style.color = 'var(--color-text-tertiary)';
    }
}

// ===================================
// CREDENTIALS MANAGEMENT
// ===================================
function saveCredentials() {
    state.credentials = {
        url: elements.webmailUrl.value,
        email: elements.emailLogin.value,
        password: elements.emailPassword.value
    };

    // Save to localStorage (except password for security)
    localStorage.setItem('webmailUrl', state.credentials.url);
    localStorage.setItem('emailLogin', state.credentials.email);

    showToast('Credenciais salvas', 'Suas credenciais foram salvas localmente', 'success');
}

function loadCredentialsFromStorage() {
    const savedUrl = localStorage.getItem('webmailUrl');
    const savedEmail = localStorage.getItem('emailLogin');

    if (savedUrl) {
        elements.webmailUrl.value = savedUrl;
        state.credentials.url = savedUrl;
    }

    if (savedEmail) {
        elements.emailLogin.value = savedEmail;
        state.credentials.email = savedEmail;
    }
}

// ===================================
// STATUS MANAGEMENT
// ===================================
function updateStatus(text, type = 'success') {
    const statusText = elements.statusBadge.querySelector('.status-text');
    const statusDot = elements.statusBadge.querySelector('.status-dot');

    statusText.textContent = text;

    const colors = {
        success: 'var(--color-success)',
        error: 'var(--color-error)',
        warning: 'var(--color-warning)',
        info: 'var(--color-primary)'
    };

    statusDot.style.background = colors[type] || colors.success;
    statusDot.style.boxShadow = `0 0 10px ${colors[type] || colors.success}`;
}

// ===================================
// TOAST NOTIFICATIONS
// ===================================
function showToast(title, message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: `<path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`,
        error: `<path d="M12 8V12M12 16H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`,
        warning: `<path d="M12 9V13M12 17H12.01M10.29 3.86L1.82 18C1.64537 18.3024 1.55296 18.6453 1.55199 18.9945C1.55101 19.3437 1.64151 19.6871 1.81445 19.9905C1.98738 20.2939 2.23675 20.5467 2.53773 20.7239C2.83871 20.9011 3.18082 20.9962 3.53 21H20.47C20.8192 20.9962 21.1613 20.9011 21.4623 20.7239C21.7633 20.5467 22.0126 20.2939 22.1856 19.9905C22.3585 19.6871 22.449 19.3437 22.448 18.9945C22.447 18.6453 22.3546 18.3024 22.18 18L13.71 3.86C13.5317 3.56611 13.2807 3.32312 12.9812 3.15448C12.6817 2.98585 12.3437 2.89725 12 2.89725C11.6563 2.89725 11.3183 2.98585 11.0188 3.15448C10.7193 3.32312 10.4683 3.56611 10.29 3.86Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`,
        info: `<path d="M13 16H12V12H11M12 8H12.01M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`
    };

    toast.innerHTML = `
        <svg class="toast-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            ${icons[type] || icons.info}
        </svg>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </button>
    `;

    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
        toast.style.animation = 'slideIn 0.25s reverse';
        setTimeout(() => toast.remove(), 250);
    });

    elements.toastContainer.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.animation = 'slideIn 0.25s reverse';
            setTimeout(() => toast.remove(), 250);
        }
    }, 5000);
}

// ===================================
// MODAL
// ===================================
function showModal(title, body, onConfirm = null) {
    elements.modalTitle.textContent = title;
    elements.modalBody.innerHTML = body;
    elements.modal.classList.remove('hidden');

    if (onConfirm) {
        elements.modalConfirm.onclick = () => {
            onConfirm();
            closeModal();
        };
    } else {
        elements.modalFooter.style.display = 'none';
    }
}

function closeModal() {
    elements.modal.classList.add('hidden');
    elements.modalFooter.style.display = 'flex';
}

// ===================================
// MAIN ACTIONS
// ===================================
async function testConnection() {
    updateStatus('Testando...', 'info');
    elements.testBtn.disabled = true;

    // Validate credentials (senha pode estar no .env)
    if (!elements.webmailUrl.value || !elements.emailLogin.value) {
        showToast('Erro', 'Preencha URL e Email (senha pode estar no .env)', 'error');
        addLog('❌ Erro: Preencha URL e Email', 'error');
        updateStatus('Erro', 'error');
        elements.testBtn.disabled = false;
        return;
    }

    try {
        addLog('🚀 Iniciando teste de conexão...', 'info');
        addLog(`📧 Email: ${elements.emailLogin.value}`, 'step');
        addLog('🌐 Abrindo navegador Chrome...', 'step');
        showToast('Conectando', 'Abrindo navegador Chrome...', 'info');

        const response = await fetch('/api/test-connection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: elements.webmailUrl.value,
                email: elements.emailLogin.value,
                password: elements.emailPassword.value
            })
        });

        const result = await response.json();

        if (result.success) {
            addLog('🔐 Fazendo login no webmail...', 'step');
            addLog('✅ ' + result.message, 'success');
            showToast('Conexão OK', result.message, 'success');
            updateStatus('Conectado', 'success');
        } else {
            addLog('❌ ' + result.message, 'error');
            showToast('Erro', result.message, 'error');
            updateStatus('Erro', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        addLog('❌ Erro de conexão: ' + error.message, 'error');
        showToast('Erro', 'Erro: ' + error.message, 'error');
        updateStatus('Erro', 'error');
    } finally {
        elements.testBtn.disabled = false;
    }
}

async function sendEmails() {
    // Validate credentials (senha pode estar no .env)
    if (!elements.webmailUrl.value || !elements.emailLogin.value) {
        showToast('Erro', 'Preencha URL e Email (senha pode estar no .env)', 'error');
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
}

function sendSingleEmail() {
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
        `,
        async () => {
            updateStatus('Enviando...', 'info');
            showToast('Enviando', 'Abrindo navegador e enviando email...', 'info');

            addLog('📧 Iniciando envio de email...', 'info');
            addLog(`📬 Destinatário: ${data.recipient}`, 'step');
            addLog(`📝 Assunto: ${data.subject}`, 'step');
            addLog('🌐 Verificando conexão com webmail...', 'step');

            try {
                addLog('📤 Enviando dados para o servidor...', 'step');

                const response = await fetch('/api/send-email', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (result.success) {
                    addLog('✅ ' + result.message, 'success');
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
                    addLog('❌ ' + result.message, 'error');
                    showToast('Erro', result.message, 'error');
                    updateStatus('Erro', 'error');
                }
            } catch (error) {
                console.error('Erro:', error);
                addLog('❌ Erro ao enviar: ' + error.message, 'error');
                showToast('Erro', 'Erro: ' + error.message, 'error');
                updateStatus('Erro', 'error');
            }
        }
    );
}

function sendBatchEmails(emails) {
    const data = {
        mode: 'batch',
        credentials: {
            url: elements.webmailUrl.value,
            email: elements.emailLogin.value,
            password: elements.emailPassword.value
        },
        recipients: emails,
        subject: elements.batchSubject.value,
        message: elements.batchMessage.value,
        files: state.files.batch
    };

    showModal(
        'Confirmar Envio em Lote',
        `
            <p>Você está prestes a enviar <strong>${emails.length} emails</strong>.</p>
            <p style="margin-top: 0.5rem;">Assunto: ${data.subject}</p>
            <div style="margin-top: 1rem; padding: 0.75rem; background: var(--color-bg-secondary); border-radius: var(--radius-sm); font-size: 0.875rem;">
                <p>⚠️ O navegador será aberto e controlado automaticamente.</p>
                <p>⚠️ Não use o computador enquanto o processo estiver rodando.</p>
            </div>
            <div id="progressContainer" style="margin-top: 1rem; display: none;">
                <div style="background: var(--color-bg-tertiary); height: 8px; border-radius: 4px; overflow: hidden;">
                    <div id="progressBar" style="width: 0%; height: 100%; background: var(--color-primary); transition: width 0.3s;"></div>
                </div>
                <p id="progressText" style="text-align: center; font-size: 0.8rem; margin-top: 0.5rem; color: var(--color-text-secondary);">Iniciando...</p>
            </div>
        `,
        async () => {
            updateStatus('Iniciando...', 'info');
            showToast('Enviando', `Iniciando envio para ${emails.length} destinatários...`, 'info');

            addLog(`📚 Iniciando envio em lote para ${emails.length} destinatários`, 'info');
            addLog(`📝 Assunto: ${data.subject}`, 'step');

            // Iniciar Polling
            const pollInterval = setInterval(pollProgress, 1000);

            try {
                // TODO: Chamar automation real
                // Por enquanto, backend já implementa a automação real na rota /api/send-email

                const response = await fetch('/api/send-email', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (result.success) {
                    const stats = result.stats || {}; // stats pode não vir no batch antigo, mas adicionei no novo
                    addLog('✅ ' + result.message, 'success');
                    if (result.sent !== undefined) addLog(`📤 Enviados: ${result.sent}`, 'success');
                    if (result.failed !== undefined) addLog(`❌ Falhas: ${result.failed}`, result.failed > 0 ? 'warning' : 'success');

                    showToast('Sucesso', result.message, 'success');
                    updateStatus('Concluído', 'success');

                    // Clear form
                    elements.recipientList.value = '';
                    elements.batchSubject.value = '';
                    elements.batchMessage.value = '';
                    elements.batchAttachment.value = '';
                    elements.batchFileList.innerHTML = '';
                    state.files.batch = [];
                } else {
                    addLog('❌ ' + result.message, 'error');
                    showToast('Erro', result.message, 'error');
                    updateStatus('Erro', 'error');
                }
            } catch (error) {
                console.error('Erro:', error);
                addLog('❌ Erro no envio em lote: ' + error.message, 'error');
                showToast('Erro', 'Erro: ' + error.message, 'error');
                updateStatus('Erro', 'error');
            } finally {
                clearInterval(pollInterval);
            }
        }
    );
}

function sendAutoEmails() {
    const data = {
        mode: 'auto',
        credentials: {
            url: elements.webmailUrl.value,
            email: elements.emailLogin.value,
            password: elements.emailPassword.value
        },
        subject: elements.autoSubject.value,
        message: elements.autoMessage.value
    };

    showModal(
        'Confirmar Envio Automático',
        `
            <p>O sistema irá processar todos os arquivos na pasta <code>anexos/</code>.</p>
            <p style="margin-top: 1rem; color: var(--color-text-secondary);">Assunto: ${data.subject}</p>
            <p style="margin-top: 0.5rem; color: var(--color-text-secondary);">Cada arquivo será enviado para o email correspondente ao nome do arquivo.</p>
        `,
        async () => {
            updateStatus('Enviando...', 'info');
            showToast('Enviando', 'Processando envios automáticos...', 'info');

            addLog('🤖 Iniciando modo de envio automático', 'info');
            addLog(`📝 Assunto: ${data.subject}`, 'step');
            addLog('📂 Verificando arquivos na pasta anexos/', 'step');

            // Iniciar Polling
            const pollInterval = setInterval(pollProgress, 1000);

            try {
                addLog('📤 Iniciando processamento...', 'step');

                const response = await fetch('/api/send-email', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (result.success) {
                    const stats = result.stats || {};
                    addLog(`✅ Processamento concluído!`, 'success');
                    addLog(`📤 Enviados: ${stats.sent || 0}`, 'success');
                    addLog(`❌ Falhas: ${stats.failed || 0}`, stats.failed > 0 ? 'warning' : 'success');

                    showToast('Sucesso', result.message, 'success');
                    updateStatus('Concluído', 'success');
                } else {
                    addLog('❌ ' + result.message, 'error');
                    showToast('Erro', result.message, 'error');
                    updateStatus('Erro', 'error');
                }
            } catch (error) {
                console.error('Erro:', error);
                addLog('❌ Erro no envio automático: ' + error.message, 'error');
                showToast('Erro', 'Erro: ' + error.message, 'error');
                updateStatus('Erro', 'error');
            } finally {
                clearInterval(pollInterval);
            }
        }
    );
}

// ===================================
// ORGANIZER FUNCTIONS
// ===================================
async function loadTriagemFiles() {
    try {
        const response = await fetch('/api/triagem/files');
        const data = await response.json();

        elements.triagemList.innerHTML = '';

        if (data.success && data.files.length > 0) {
            data.files.forEach(file => {
                const item = document.createElement('div');
                item.className = 'sidebar-item';
                item.innerHTML = `
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <span class="sidebar-item-name">${file}</span>
                `;
                item.onclick = (e) => selectTriagemFile(file, item, e);
                elements.triagemList.appendChild(item);
            });
        } else {
            elements.triagemList.innerHTML = '<div class="empty-list">Nenhum arquivo encontrado</div>';
        }
    } catch (error) {
        console.error('Erro ao carregar arquivos:', error);
        showToast('Erro', 'Falha ao carregar lista de arquivos', 'error');
    }
}

function selectTriagemFile(filename, element, event) {
    if (event && (event.ctrlKey || event.metaKey)) {
        // Toggle selection
        if (state.selectedTriagemFiles.has(filename)) {
            state.selectedTriagemFiles.delete(filename);
            element.classList.remove('active');
        } else {
            state.selectedTriagemFiles.add(filename);
            element.classList.add('active');
        }
    } else {
        // Single selection
        state.selectedTriagemFiles.clear();
        state.selectedTriagemFiles.add(filename);
        document.querySelectorAll('.sidebar-item').forEach(el => el.classList.remove('active'));
        element.classList.add('active');
    }

    const count = state.selectedTriagemFiles.size;

    if (count === 0) {
        elements.filePreview.innerHTML = '<div class="preview-placeholder"><p>Selecione um arquivo</p></div>';
        elements.organizerControls.classList.add('disabled');
        state.currentTriagemFile = null;
        return;
    }

    elements.organizerControls.classList.remove('disabled');

    // Preview logic
    if (count === 1) {
        // Show preview for single file
        const file = Array.from(state.selectedTriagemFiles)[0];
        const encoded = encodeURIComponent(file);
        elements.filePreview.innerHTML = `
            <iframe src="/api/triagem/file/${encoded}" class="preview-iframe"></iframe>
        `;
        state.currentTriagemFile = file; // Backward compatibility/convenience
    } else {
        // Multi-file summary
        elements.filePreview.innerHTML = `
            <div class="preview-placeholder">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 48px; height: 48px; margin-bottom: 1rem;"><path d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                <h3>${count} arquivos selecionados</h3>
                <ul style="text-align: left; margin-top: 1rem; color: var(--color-text-secondary);">
                    ${Array.from(state.selectedTriagemFiles).map(f => `<li>${f}</li>`).join('')}
                </ul>
            </div>
        `;
        state.currentTriagemFile = null;
    }

    elements.organizerEmail.focus();
}

async function scanEmail() {
    const count = state.selectedTriagemFiles.size;
    if (count === 0) {
        showToast('Atenção', 'Selecione um arquivo para escanear', 'warning');
        return;
    }

    // Scan first file
    const filename = Array.from(state.selectedTriagemFiles)[0];

    updateStatus('Escaneando...', 'info');
    showToast('Scan', 'Procurando email no arquivo...', 'info');

    try {
        const response = await fetch('/api/triagem/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename })
        });
        const result = await response.json();

        if (result.success) {
            elements.organizerEmail.value = result.email;
            showToast('Sucesso', 'Email detectado: ' + result.email, 'success');
            addLog(`🔍 Email detectado em ${filename}: ${result.email}`, 'info');
            updateStatus('Email Detectado', 'success');
        } else {
            showToast('Aviso', result.message, 'warning');
            updateStatus('Não encontrado', 'warning');
        }
    } catch (error) {
        console.error('Erro no scan:', error);
        showToast('Erro', 'Falha ao escanear arquivo', 'error');
        updateStatus('Erro', 'error');
    }
}

async function processTriagemFile() {
    const email = elements.organizerEmail.value;
    const count = state.selectedTriagemFiles.size;

    if (!email || count === 0) {
        showToast('Atenção', 'Selecione arquivos e digite o email', 'warning');
        return;
    }

    // Validar email simples
    if (!email.includes('@')) {
        showToast('Erro', 'Email inválido', 'error');
        return;
    }

    try {
        const filesToProcess = Array.from(state.selectedTriagemFiles);

        const response = await fetch('/api/triagem/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ files: filesToProcess, email })
        });

        const result = await response.json();

        if (result.success) {
            showToast('Sucesso', 'Arquivo movido para para envio!', 'success');
            addLog(`✅ ${state.selectedTriagemFiles.size} arquivos preparados para: ${email}`, 'success');
            loadTriagemFiles();
            state.selectedTriagemFiles.clear();
            elements.filePreview.innerHTML = '<div class="preview-placeholder"><svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg><p>Selecione um arquivo</p></div>';
            elements.organizerControls.classList.add('disabled');
            state.currentTriagemFile = null;
        } else {
            showToast('Erro', result.message, 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showToast('Erro', 'Falha ao processar arquivo', 'error');
    }
}

// ===================================
// UTILITY FUNCTIONS
// ===================================
function viewLogs() {
    showModal(
        'Logs de Envio',
        `
            <div style="font-family: 'Courier New', monospace; font-size: 0.875rem; background: var(--color-bg); padding: 1rem; border-radius: var(--radius-md); max-height: 400px; overflow-y: auto;">
                <p>[05/02/2026 09:30:15] Para: cliente1@email.com | Assunto: Documentos | Status: SUCESSO</p>
                <p>[05/02/2026 09:30:22] Para: cliente2@email.com | Assunto: Documentos | Status: SUCESSO</p>
                <p>[05/02/2026 09:30:28] Para: cliente3@email.com | Assunto: Documentos | Status: FALHA</p>
                <p style="color: var(--color-text-tertiary); margin-top: 1rem;">Logs completos disponíveis em: logs/envios_20260205.txt</p>
            </div>
        `
    );
}

function showHelp() {
    showModal(
        'Ajuda - Como Usar',
        `
            <div style="display: flex; flex-direction: column; gap: 1.5rem;">
                <div>
                    <h4 style="color: var(--color-primary); margin-bottom: 0.5rem;">📧 Envio Único</h4>
                    <p style="font-size: 0.875rem; color: var(--color-text-secondary);">
                        Envie um email para um único destinatário. Preencha o destinatário, assunto, mensagem e anexos opcionais.
                    </p>
                </div>
                
                <div>
                    <h4 style="color: var(--color-primary); margin-bottom: 0.5rem;">📋 Envio em Lote</h4>
                    <p style="font-size: 0.875rem; color: var(--color-text-secondary);">
                        Envie o mesmo email para múltiplos destinatários. Digite um email por linha na lista de destinatários.
                    </p>
                </div>
                
                <div>
                    <h4 style="color: var(--color-primary); margin-bottom: 0.5rem;">⚡ Envio Automático</h4>
                    <p style="font-size: 0.875rem; color: var(--color-text-secondary);">
                        Coloque arquivos na pasta <code>anexos/</code> nomeados com o email do destinatário (ex: cliente@email.com.pdf). O sistema enviará automaticamente.
                    </p>
                </div>
                
                <div style="padding: 1rem; background: var(--color-bg-secondary); border-radius: var(--radius-md); border-left: 4px solid var(--color-warning);">
                    <p style="font-size: 0.875rem; color: var(--color-text-secondary);">
                        <strong>⚠️ Dica:</strong> Sempre teste com "Envio Único" antes de usar envios em lote ou automáticos.
                    </p>
                </div>
            </div>
        `
    );
}

// ===================================
// PROGRESS POLLING
// ===================================
async function pollProgress() {
    try {
        const response = await fetch('/api/progress');
        const data = await response.json();

        if (data.status === 'running') {
            const pct = data.total > 0 ? Math.round((data.current / data.total) * 100) : 0;
            updateStatus(`${data.current}/${data.total} (${pct}%) - ${data.message}`, 'info');
        }
    } catch (error) {
        console.error('Erro no polling:', error);
    }
}

function showPreview() {
    const mode = state.currentMode;
    let content = '';

    if (mode === 'single') {
        const recipient = elements.recipient.value || '<span style="color: var(--color-text-tertiary)">(vazio)</span>';
        const subject = elements.subject.value || '<span style="color: var(--color-text-tertiary)">(vazio)</span>';
        const message = elements.message.value
            ? elements.message.value.replace(/\n/g, '<br>')
            : '<span style="color: var(--color-text-tertiary)">(vazio)</span>';

        content = `
            <div style="display: flex; flex-direction: column; gap: 1rem;">
                <div>
                    <strong>Para:</strong> ${recipient}
                </div>
                <div>
                    <strong>Assunto:</strong> ${subject}
                </div>
                <hr style="border: 0; border-top: 1px solid var(--color-divider);">
                <div style="background: var(--color-bg-secondary); padding: 1rem; border-radius: var(--radius-md);">
                    ${message}
                </div>
            </div>
        `;
    } else if (mode === 'batch') {
        const emails = elements.recipientList.value.split('\n').filter(l => l.trim());
        const count = emails.length;
        const subject = elements.batchSubject.value || '<span style="color: var(--color-text-tertiary)">(vazio)</span>';
        const message = elements.batchMessage.value
            ? elements.batchMessage.value.replace(/\n/g, '<br>')
            : '<span style="color: var(--color-text-tertiary)">(vazio)</span>';

        content = `
            <div style="display: flex; flex-direction: column; gap: 1rem;">
                <div>
                    <strong>Para:</strong> ${count} destinatários (Lista)
                    <div style="max-height: 100px; overflow-y: auto; font-size: 0.8rem; margin-top: 0.5rem; color: var(--color-text-secondary);">
                        ${emails.slice(0, 5).join('<br>')}
                        ${count > 5 ? `<br>... e mais ${count - 5}` : ''}
                    </div>
                </div>
                <div>
                    <strong>Assunto:</strong> ${subject}
                </div>
                <hr style="border: 0; border-top: 1px solid var(--color-divider);">
                <div style="background: var(--color-bg-secondary); padding: 1rem; border-radius: var(--radius-md);">
                    ${message}
                </div>
            </div>
        `;
    } else {
        showToast('Info', 'Preview indisponível neste modo', 'info');
        return;
    }

    showModal('Pré-visualização do Email', content, null);
}

// ===================================
// LOAD CREDENTIALS FROM .ENV
// ===================================
async function loadCredentialsFromEnv() {
    try {
        addLog('🔄 Carregando credenciais do arquivo .env...', 'info');

        const response = await fetch('/api/credentials');
        const data = await response.json();

        if (data.success && data.credentials) {
            const creds = data.credentials;

            // Preencher campos com dados do .env
            if (creds.url) {
                elements.webmailUrl.value = creds.url;
                state.credentials.url = creds.url;
                addLog('🌐 URL do webmail carregada', 'step');
            }

            if (creds.email) {
                elements.emailLogin.value = creds.email;
                state.credentials.email = creds.email;
                addLog(`📧 Email carregado: ${creds.email}`, 'step');
            }

            // Carregar assunto e mensagem padrão do template
            if (creds.defaultSubject) {
                elements.subject.value = creds.defaultSubject;
                elements.batchSubject.value = creds.defaultSubject;
                elements.autoSubject.value = creds.defaultSubject;
                addLog(`📝 Assunto padrão: ${creds.defaultSubject}`, 'step');
            }

            if (creds.defaultMessage) {
                elements.message.value = creds.defaultMessage;
                elements.batchMessage.value = creds.defaultMessage;
                elements.autoMessage.value = creds.defaultMessage;
                addLog('📄 Mensagem padrão carregada do template', 'step');
            }

            // Se há senha no .env, mostrar indicação visual
            if (creds.hasPassword) {
                elements.emailPassword.placeholder = '••••••••  (configurada no .env)';
                elements.emailPassword.style.borderColor = 'var(--color-success)';
                addLog('🔐 Senha detectada no .env', 'step');

                // Adicionar tooltip informativo
                const passwordGroup = elements.emailPassword.closest('.form-group');
                const existingHint = passwordGroup.querySelector('.form-hint');
                if (!existingHint) {
                    const hint = document.createElement('div');
                    hint.className = 'form-hint';
                    hint.style.color = 'var(--color-success)';
                    hint.innerHTML = `
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        <span>Senha carregada do arquivo .env</span>
                    `;
                    passwordGroup.appendChild(hint);
                }
            }

            // Mostrar sucesso se carregou credenciais
            if (creds.url && creds.email) {
                addLog('✅ Configurações sincronizadas com CLI!', 'success');
                showToast('Configurações Carregadas', 'Credenciais e template sincronizados com CLI', 'success');
            }
        }
    } catch (error) {
        console.error('Erro ao carregar credenciais do .env:', error);
        addLog('⚠️ Erro ao carregar credenciais: ' + error.message, 'warning');
        // Fallback para localStorage se API falhar
        loadCredentialsFromStorage();
    }
}

// ===================================
// START APPLICATION
// ===================================
document.addEventListener('DOMContentLoaded', init);

// ===================================
// DRAG AND DROP
// ===================================
document.body.addEventListener('dragover', (e) => {
    e.preventDefault();
    if (state.currentMode === 'organizer') {
        const overlay = document.getElementById('dropOverlay');
        if (overlay) overlay.classList.remove('hidden');
    }
});

document.body.addEventListener('dragleave', (e) => {
    if (e.relatedTarget === null) {
        const overlay = document.getElementById('dropOverlay');
        if (overlay) overlay.classList.add('hidden');
    }
});

document.body.addEventListener('drop', async (e) => {
    e.preventDefault();
    const overlay = document.getElementById('dropOverlay');
    if (overlay) overlay.classList.add('hidden');

    if (state.currentMode === 'organizer') {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            uploadFilesToTriagem(files);
        }
    }
});

async function uploadFilesToTriagem(files) {
    const formData = new FormData();
    for (const file of files) {
        formData.append('files[]', file);
    }

    updateStatus('Enviando arquivos...', 'info');
    showToast('Upload', `Enviando ${files.length} arquivos para triagem...`, 'info');

    try {
        const response = await fetch('/api/triagem/upload', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();

        if (result.success) {
            showToast('Sucesso', result.message, 'success');
            loadTriagemFiles(); // Recarregar lista
            updateStatus('Concluído', 'success');
        } else {
            showToast('Erro', result.message, 'error');
            updateStatus('Erro', 'error');
        }
    } catch (error) {
        console.error(error);
        showToast('Erro', 'Falha no upload', 'error');
        updateStatus('Erro', 'error');
    }
}

// ===================================
// CONTACTS MANAGEMENT
// ===================================
async function loadContacts() {
    try {
        const response = await fetch('/api/contacts');
        const contacts = await response.json();

        renderContacts(contacts);
    } catch (error) {
        console.error('Erro ao carregar contatos:', error);
        showToast('Erro', 'Falha ao carregar contatos', 'error');
    }
}

function renderContacts(contacts) {
    const tbody = elements.contactsTable.querySelector('tbody');
    tbody.innerHTML = '';

    if (!contacts || contacts.length === 0) {
        elements.noContactsMessage.classList.remove('hidden');
        elements.contactsTable.classList.add('hidden');
        return;
    }

    elements.noContactsMessage.classList.add('hidden');
    elements.contactsTable.classList.remove('hidden');

    contacts.forEach(contact => {
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid var(--color-border)';

        tr.innerHTML = `
            <td style="padding: 1rem;">${contact.name}</td>
            <td style="padding: 1rem;">${contact.email}</td>
            <td style="padding: 1rem; text-align: right;">
                <button class="btn-icon-small" onclick="deleteContact('${contact.email}')" title="Excluir" style="color: var(--color-error);">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 18px; height: 18px;"><path d="M18 6L6 18M6 6L18 18"/></svg>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function showAddContactModal() {
    showModal(
        'Adicionar Contato',
        `
            <div class="form-group">
                <label class="form-label">Nome</label>
                <input type="text" id="newContactName" class="form-input" placeholder="Ex: João Silva">
            </div>
            <div class="form-group">
                <label class="form-label">Email</label>
                <input type="email" id="newContactEmail" class="form-input" placeholder="Ex: joao@emplo.com">
            </div>
        `,
        async () => {
            const name = document.getElementById('newContactName').value;
            const email = document.getElementById('newContactEmail').value;

            if (!name || !email) {
                showToast('Erro', 'Preencha nome e email', 'warning');
                return;
            }

            if (!validateEmail(email)) {
                showToast('Erro', 'Email inválido', 'warning');
                return;
            }

            await addContact(name, email);
        }
    );
}

async function addContact(name, email) {
    try {
        const response = await fetch('/api/contacts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email })
        });
        const result = await response.json();

        if (result.success) {
            showToast('Sucesso', 'Contato adicionado!', 'success');
            loadContacts();
        } else {
            showToast('Erro', result.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao adicionar contato:', error);
        showToast('Erro', 'Falha na requisição', 'error');
    }
}

async function deleteContact(email) {
    if (!confirm(`Tem certeza que deseja remover o contato ${email}?`)) return;

    try {
        const response = await fetch(`/api/contacts/${email}`, {
            method: 'DELETE'
        });
        const result = await response.json();

        if (result.success) {
            showToast('Sucesso', 'Contato removido', 'success');
            loadContacts();
        } else {
            showToast('Erro', result.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao remover contato:', error);
        showToast('Erro', 'Falha na requisição', 'error');
    }
}

// ===================================
// REPORTS
// ===================================
async function downloadReport() {
    updateStatus('Gerando relatório...', 'info');
    showToast('Relatório', 'Preparando relatório PDF de hoje...', 'info');

    try {
        const response = await fetch('/api/reports/daily');

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Relatorio_Envios_${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showToast('Sucesso', 'Relatório baixado com sucesso!', 'success');
            updateStatus('Pronto', 'success');
        } else {
            const result = await response.json();
            showToast('Erro', result.message || 'Falha ao gerar relatório', 'error');
            updateStatus('Erro', 'error');
        }
    } catch (error) {
        console.error('Erro ao baixar relatório:', error);
        showToast('Erro', 'Erro na conexão com o servidor', 'error');
        updateStatus('Erro', 'error');
    }
}

