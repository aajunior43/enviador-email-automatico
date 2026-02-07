// ===================================
// PROGRESS INDICATOR COMPONENTS
// ===================================

class ProgressBar {
    constructor(container, options = {}) {
        this.container = typeof container === 'string' ? document.getElementById(container) : container;
        this.options = {
            showPercentage: true,
            showCounter: true,
            showTime: true,
            animated: true,
            ...options
        };
        this.total = 0;
        this.current = 0;
        this.startTime = null;
        this.element = null;
        this.init();
    }

    init() {
        if (!this.container) return;
        
        this.element = document.createElement('div');
        this.element.className = 'progress-wrapper';
        this.element.innerHTML = `
            <div class="progress-header">
                <div class="progress-info">
                    <span class="progress-counter">0 / 0</span>
                    <span class="progress-percentage">0%</span>
                </div>
                <div class="progress-time">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    <span class="progress-time-text">Calculando...</span>
                </div>
            </div>
            <div class="progress-bar">
                <div class="progress-bar-fill" style="width: 0%"></div>
            </div>
            <div class="progress-status">Preparando...</div>
        `;
        
        this.container.appendChild(this.element);
        this.elements = {
            counter: this.element.querySelector('.progress-counter'),
            percentage: this.element.querySelector('.progress-percentage'),
            time: this.element.querySelector('.progress-time-text'),
            fill: this.element.querySelector('.progress-bar-fill'),
            status: this.element.querySelector('.progress-status'),
            timeContainer: this.element.querySelector('.progress-time')
        };

        if (!this.options.showCounter) this.elements.counter.style.display = 'none';
        if (!this.options.showPercentage) this.elements.percentage.style.display = 'none';
        if (!this.options.showTime) this.elements.timeContainer.style.display = 'none';
    }

    start(total) {
        this.total = total;
        this.current = 0;
        this.startTime = Date.now();
        this.update(0);
    }

    update(current, status = null) {
        this.current = current;
        const percentage = this.total > 0 ? Math.round((current / this.total) * 100) : 0;
        
        if (this.options.showCounter) {
            this.elements.counter.textContent = `${current} / ${this.total}`;
        }
        
        if (this.options.showPercentage) {
            this.elements.percentage.textContent = `${percentage}%`;
        }
        
        this.elements.fill.style.width = `${percentage}%`;
        
        if (this.options.showTime && this.startTime && current > 0) {
            const elapsed = Date.now() - this.startTime;
            const avgTimePerItem = elapsed / current;
            const remaining = (this.total - current) * avgTimePerItem;
            this.elements.time.textContent = this.formatTime(remaining);
        }
        
        if (status) {
            this.elements.status.textContent = status;
        }
    }

    complete(message = 'Concluído!') {
        this.update(this.total, message);
        this.elements.fill.classList.add('progress-complete');
        if (this.options.showTime) {
            const elapsed = Date.now() - this.startTime;
            this.elements.time.textContent = `Total: ${this.formatTime(elapsed)}`;
        }
    }

    error(message = 'Erro ao processar') {
        this.elements.status.textContent = message;
        this.elements.fill.classList.add('progress-error');
    }

    formatTime(ms) {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        
        if (hours > 0) {
            return `${hours}h ${minutes % 60}m`;
        } else if (minutes > 0) {
            return `${minutes}m ${seconds % 60}s`;
        } else {
            return `${seconds}s`;
        }
    }

    destroy() {
        if (this.element && this.element.parentElement) {
            this.element.parentElement.removeChild(this.element);
        }
    }
}

class CircularProgress {
    constructor(container, options = {}) {
        this.container = typeof container === 'string' ? document.getElementById(container) : container;
        this.options = {
            size: 120,
            strokeWidth: 8,
            showPercentage: true,
            ...options
        };
        this.percentage = 0;
        this.init();
    }

    init() {
        if (!this.container) return;
        
        const { size, strokeWidth } = this.options;
        const radius = (size - strokeWidth) / 2;
        const circumference = radius * 2 * Math.PI;
        
        this.element = document.createElement('div');
        this.element.className = 'circular-progress';
        this.element.innerHTML = `
            <svg width="${size}" height="${size}" class="circular-progress-svg">
                <circle
                    class="circular-progress-bg"
                    cx="${size / 2}"
                    cy="${size / 2}"
                    r="${radius}"
                    stroke-width="${strokeWidth}"
                />
                <circle
                    class="circular-progress-fill"
                    cx="${size / 2}"
                    cy="${size / 2}"
                    r="${radius}"
                    stroke-width="${strokeWidth}"
                    stroke-dasharray="${circumference}"
                    stroke-dashoffset="${circumference}"
                />
            </svg>
            ${this.options.showPercentage ? `<div class="circular-progress-text">0%</div>` : ''}
        `;
        
        this.container.appendChild(this.element);
        this.fillCircle = this.element.querySelector('.circular-progress-fill');
        this.textElement = this.element.querySelector('.circular-progress-text');
        this.circumference = circumference;
    }

    update(percentage) {
        this.percentage = Math.min(100, Math.max(0, percentage));
        const offset = this.circumference - (this.percentage / 100) * this.circumference;
        
        if (this.fillCircle) {
            this.fillCircle.style.strokeDashoffset = offset;
        }
        
        if (this.textElement) {
            this.textElement.textContent = `${Math.round(this.percentage)}%`;
        }
    }

    complete() {
        this.update(100);
        this.fillCircle.classList.add('progress-complete');
    }

    destroy() {
        if (this.element && this.element.parentElement) {
            this.element.parentElement.removeChild(this.element);
        }
    }
}

window.ProgressBar = ProgressBar;
window.CircularProgress = CircularProgress;
