// ===================================
// VALIDATION UTILITIES
// ===================================

class Validator {
    static isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }

    static validateEmailList(emailString) {
        const emails = emailString.split(/[,;\n]/).map(e => e.trim()).filter(e => e);
        const valid = [];
        const invalid = [];
        
        emails.forEach(email => {
            if (this.isValidEmail(email)) {
                valid.push(email);
            } else {
                invalid.push(email);
            }
        });
        
        return { valid, invalid, total: emails.length };
    }

    static checkPasswordStrength(password) {
        let strength = 0;
        const feedback = [];
        
        if (!password) {
            return { strength: 0, label: 'Vazia', feedback: ['Digite uma senha'], color: 'var(--color-error)' };
        }
        
        // Length
        if (password.length >= 8) {
            strength += 25;
        } else {
            feedback.push('Mínimo 8 caracteres');
        }
        
        // Uppercase
        if (/[A-Z]/.test(password)) {
            strength += 25;
        } else {
            feedback.push('Adicione maiúsculas');
        }
        
        // Lowercase
        if (/[a-z]/.test(password)) {
            strength += 25;
        } else {
            feedback.push('Adicione minúsculas');
        }
        
        // Numbers or Special
        if (/[0-9]/.test(password)) {
            strength += 15;
        }
        if (/[^A-Za-z0-9]/.test(password)) {
            strength += 10;
        }
        if (!/[0-9]/.test(password) && !/[^A-Za-z0-9]/.test(password)) {
            feedback.push('Adicione números ou símbolos');
        }
        
        // Determine label and color
        let label, color;
        if (strength < 30) {
            label = 'Fraca';
            color = 'var(--color-error)';
        } else if (strength < 60) {
            label = 'Média';
            color = 'var(--color-warning)';
        } else if (strength < 90) {
            label = 'Boa';
            color = '#3498db';
        } else {
            label = 'Forte';
            color = 'var(--color-success)';
        }
        
        return { strength, label, feedback, color };
    }

    static validateURL(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    static isEmpty(value) {
        return !value || value.trim() === '';
    }
}

// Real-time Email Validation Component
class EmailValidator {
    constructor(inputElement, options = {}) {
        this.input = inputElement;
        this.options = {
            showIcon: true,
            showMessage: true,
            validateOnType: true,
            debounceTime: 300,
            ...options
        };
        this.timeout = null;
        this.isValid = false;
        this.init();
    }

    init() {
        if (!this.input) return;
        
        // Create feedback elements
        if (this.options.showIcon || this.options.showMessage) {
            this.input.parentElement.style.position = 'relative';
            
            if (this.options.showIcon) {
                this.iconElement = document.createElement('div');
                this.iconElement.className = 'validation-icon';
                this.input.parentElement.appendChild(this.iconElement);
            }
            
            if (this.options.showMessage) {
                this.messageElement = document.createElement('div');
                this.messageElement.className = 'validation-message';
                this.input.parentElement.appendChild(this.messageElement);
            }
        }
        
        // Add event listeners
        if (this.options.validateOnType) {
            this.input.addEventListener('input', () => this.handleInput());
        }
        this.input.addEventListener('blur', () => this.validate());
    }

    handleInput() {
        clearTimeout(this.timeout);
        this.timeout = setTimeout(() => this.validate(), this.options.debounceTime);
    }

    validate() {
        const email = this.input.value.trim();
        
        if (!email) {
            this.setStatus('neutral');
            return true;
        }
        
        this.isValid = Validator.isValidEmail(email);
        
        if (this.isValid) {
            this.setStatus('valid', 'Email válido');
        } else {
            this.setStatus('invalid', 'Email inválido');
        }
        
        return this.isValid;
    }

    setStatus(status, message = '') {
        this.input.classList.remove('input-valid', 'input-invalid');
        
        if (status === 'valid') {
            this.input.classList.add('input-valid');
            if (this.iconElement) {
                this.iconElement.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2">
                        <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                `;
            }
        } else if (status === 'invalid') {
            this.input.classList.add('input-invalid');
            if (this.iconElement) {
                this.iconElement.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-error)" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="15" y1="9" x2="9" y2="15"></line>
                        <line x1="9" y1="9" x2="15" y2="15"></line>
                    </svg>
                `;
            }
        } else {
            if (this.iconElement) {
                this.iconElement.innerHTML = '';
            }
        }
        
        if (this.messageElement) {
            this.messageElement.textContent = message;
            this.messageElement.className = `validation-message validation-${status}`;
        }
    }
}

// Password Strength Indicator
class PasswordStrengthIndicator {
    constructor(inputElement, options = {}) {
        this.input = inputElement;
        this.options = {
            showBar: true,
            showLabel: true,
            showFeedback: true,
            ...options
        };
        this.init();
    }

    init() {
        if (!this.input) return;
        
        // Create indicator container
        this.container = document.createElement('div');
        this.container.className = 'password-strength-indicator';
        
        if (this.options.showBar) {
            this.barElement = document.createElement('div');
            this.barElement.className = 'password-strength-bar';
            this.barElement.innerHTML = '<div class="password-strength-bar-fill"></div>';
            this.container.appendChild(this.barElement);
            this.barFill = this.barElement.querySelector('.password-strength-bar-fill');
        }
        
        if (this.options.showLabel) {
            this.labelElement = document.createElement('div');
            this.labelElement.className = 'password-strength-label';
            this.container.appendChild(this.labelElement);
        }
        
        if (this.options.showFeedback) {
            this.feedbackElement = document.createElement('div');
            this.feedbackElement.className = 'password-strength-feedback';
            this.container.appendChild(this.feedbackElement);
        }
        
        this.input.parentElement.appendChild(this.container);
        
        // Add event listener
        this.input.addEventListener('input', () => this.update());
    }

    update() {
        const password = this.input.value;
        const result = Validator.checkPasswordStrength(password);
        
        if (this.barFill) {
            this.barFill.style.width = `${result.strength}%`;
            this.barFill.style.backgroundColor = result.color;
        }
        
        if (this.labelElement) {
            this.labelElement.textContent = result.label;
            this.labelElement.style.color = result.color;
        }
        
        if (this.feedbackElement && result.feedback.length > 0) {
            this.feedbackElement.innerHTML = result.feedback.map(f => 
                `<div class="feedback-item">• ${f}</div>`
            ).join('');
        } else if (this.feedbackElement) {
            this.feedbackElement.innerHTML = '';
        }
    }
}

// Confirmation Dialog for Mass Actions
function confirmMassAction(count, action = 'enviar') {
    return new Promise((resolve) => {
        if (count <= 10) {
            resolve(true);
            return;
        }
        
        const modal = document.createElement('div');
        modal.className = 'confirmation-modal';
        modal.innerHTML = `
            <div class="confirmation-overlay"></div>
            <div class="confirmation-dialog">
                <div class="confirmation-icon">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--color-warning)" stroke-width="2">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line>
                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                </div>
                <h3 class="confirmation-title">Confirmar Ação em Massa</h3>
                <p class="confirmation-message">
                    Você está prestes a ${action} <strong>${count} emails</strong>.<br>
                    Esta ação pode levar alguns minutos. Deseja continuar?
                </p>
                <div class="confirmation-actions">
                    <button class="btn btn-secondary" id="confirmCancel">Cancelar</button>
                    <button class="btn btn-primary" id="confirmOk">Confirmar e ${action}</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        modal.querySelector('#confirmOk').addEventListener('click', () => {
            document.body.removeChild(modal);
            resolve(true);
        });
        
        modal.querySelector('#confirmCancel').addEventListener('click', () => {
            document.body.removeChild(modal);
            resolve(false);
        });
        
        modal.querySelector('.confirmation-overlay').addEventListener('click', () => {
            document.body.removeChild(modal);
            resolve(false);
        });
    });
}

window.Validator = Validator;
window.EmailValidator = EmailValidator;
window.PasswordStrengthIndicator = PasswordStrengthIndicator;
window.confirmMassAction = confirmMassAction;
