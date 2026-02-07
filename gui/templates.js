// ===================================
// EMAIL TEMPLATES SYSTEM
// ===================================

class TemplateManager {
    constructor() {
        this.templates = this.loadTemplates();
        this.storageKey = 'email_templates';
    }

    loadTemplates() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : this.getDefaultTemplates();
        } catch (e) {
            console.error('Erro ao carregar templates:', e);
            return this.getDefaultTemplates();
        }
    }

    saveTemplates() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.templates));
            return true;
        } catch (e) {
            console.error('Erro ao salvar templates:', e);
            return false;
        }
    }

    getDefaultTemplates() {
        return [
            {
                id: 'welcome',
                name: 'Boas-vindas',
                subject: 'Bem-vindo(a) à {empresa}!',
                body: 'Olá {nome},\n\nÉ com grande prazer que damos as boas-vindas a você!\n\nEstamos muito felizes em tê-lo(a) conosco.\n\nAtenciosamente,\nEquipe {empresa}',
                category: 'geral',
                variables: ['nome', 'empresa']
            },
            {
                id: 'follow-up',
                name: 'Follow-up',
                subject: 'Acompanhamento - {assunto}',
                body: 'Olá {nome},\n\nEspero que esteja bem!\n\nEstou entrando em contato para dar um retorno sobre {assunto}.\n\n{mensagem}\n\nFico à disposição para qualquer esclarecimento.\n\nAtenciosamente,\n{remetente}',
                category: 'comercial',
                variables: ['nome', 'assunto', 'mensagem', 'remetente']
            },
            {
                id: 'invoice',
                name: 'Envio de Fatura',
                subject: 'Fatura #{numero} - {empresa}',
                body: 'Prezado(a) {nome},\n\nSegue anexo a fatura #{numero} referente aos serviços prestados.\n\nValor: R$ {valor}\nVencimento: {vencimento}\n\nPara qualquer dúvida, estamos à disposição.\n\nAtenciosamente,\nFinanceiro - {empresa}',
                category: 'financeiro',
                variables: ['nome', 'numero', 'empresa', 'valor', 'vencimento']
            }
        ];
    }

    getAll() {
        return this.templates;
    }

    getById(id) {
        return this.templates.find(t => t.id === id);
    }

    getByCategory(category) {
        return this.templates.filter(t => t.category === category);
    }

    create(template) {
        const newTemplate = {
            id: this.generateId(),
            name: template.name,
            subject: template.subject,
            body: template.body,
            category: template.category || 'personalizado',
            variables: this.extractVariables(template.subject + ' ' + template.body),
            createdAt: new Date().toISOString()
        };
        
        this.templates.push(newTemplate);
        this.saveTemplates();
        return newTemplate;
    }

    update(id, updates) {
        const index = this.templates.findIndex(t => t.id === id);
        if (index === -1) return null;
        
        this.templates[index] = {
            ...this.templates[index],
            ...updates,
            variables: this.extractVariables(updates.subject + ' ' + updates.body),
            updatedAt: new Date().toISOString()
        };
        
        this.saveTemplates();
        return this.templates[index];
    }

    delete(id) {
        const index = this.templates.findIndex(t => t.id === id);
        if (index === -1) return false;
        
        this.templates.splice(index, 1);
        this.saveTemplates();
        return true;
    }

    generateId() {
        return 'tpl_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    extractVariables(text) {
        const regex = /{([^}]+)}/g;
        const variables = new Set();
        let match;
        
        while ((match = regex.exec(text)) !== null) {
            variables.add(match[1]);
        }
        
        return Array.from(variables);
    }

    applyTemplate(template, variables) {
        let subject = template.subject;
        let body = template.body;
        
        Object.entries(variables).forEach(([key, value]) => {
            const regex = new RegExp(`{${key}}`, 'g');
            subject = subject.replace(regex, value);
            body = body.replace(regex, value);
        });
        
        return { subject, body };
    }

    getCategories() {
        const categories = new Set(this.templates.map(t => t.category));
        return Array.from(categories);
    }
}

// Template UI Component
class TemplateUI {
    constructor(containerElement, templateManager) {
        this.container = containerElement;
        this.templateManager = templateManager;
        this.currentTemplate = null;
        this.currentVariables = {};
        this.init();
    }

    init() {
        if (!this.container) return;
        
        this.render();
        this.attachEvents();
    }

    render() {
        const templates = this.templateManager.getAll();
        const categories = this.templateManager.getCategories();
        
        this.container.innerHTML = `
            <div class="template-section">
                <div class="template-header">
                    <h3 class="template-title">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                            <line x1="16" y1="13" x2="8" y2="13"></line>
                            <line x1="16" y1="17" x2="8" y2="17"></line>
                            <polyline points="10 9 9 9 8 9"></polyline>
                        </svg>
                        Templates de Email
                    </h3>
                    <button class="btn btn-sm btn-primary" id="newTemplateBtn">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="12" y1="5" x2="12" y2="19"></line>
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                        Novo Template
                    </button>
                </div>
                
                <div class="template-filters">
                    <select class="form-select" id="categoryFilter">
                        <option value="">Todas as categorias</option>
                        ${categories.map(cat => `<option value="${cat}">${this.capitalizeFirst(cat)}</option>`).join('')}
                    </select>
                </div>
                
                <div class="template-list" id="templateList">
                    ${this.renderTemplateList(templates)}
                </div>
                
                <div class="template-preview" id="templatePreview" style="display: none;">
                    <div class="template-preview-header">
                        <h4>Aplicar Template</h4>
                        <button class="btn-icon" id="closePreview">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"></line>
                                <line x1="6" y1="6" x2="18" y2="18"></line>
                            </svg>
                        </button>
                    </div>
                    <div id="templateVariables"></div>
                    <div class="template-preview-actions">
                        <button class="btn btn-secondary" id="cancelTemplate">Cancelar</button>
                        <button class="btn btn-primary" id="applyTemplate">Aplicar Template</button>
                    </div>
                </div>
            </div>
        `;
    }

    renderTemplateList(templates) {
        if (templates.length === 0) {
            return '<div class="empty-state">Nenhum template encontrado</div>';
        }
        
        return templates.map(template => `
            <div class="template-item" data-id="${template.id}">
                <div class="template-item-header">
                    <div class="template-item-info">
                        <h4 class="template-item-name">${template.name}</h4>
                        <span class="template-item-category">${this.capitalizeFirst(template.category)}</span>
                    </div>
                    <div class="template-item-actions">
                        <button class="btn-icon use-template" data-id="${template.id}" title="Usar template">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="9 11 12 14 22 4"></polyline>
                                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                            </svg>
                        </button>
                        <button class="btn-icon edit-template" data-id="${template.id}" title="Editar">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                            </svg>
                        </button>
                        <button class="btn-icon delete-template" data-id="${template.id}" title="Excluir">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="3 6 5 6 21 6"></polyline>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                            </svg>
                        </button>
                    </div>
                </div>
                <p class="template-item-subject">${template.subject}</p>
                ${template.variables.length > 0 ? 
                    `<div class="template-item-variables">
                        Variáveis: ${template.variables.map(v => `<code>{${v}}</code>`).join(', ')}
                    </div>` : ''}
            </div>
        `).join('');
    }

    attachEvents() {
        // Use template
        this.container.addEventListener('click', (e) => {
            const useBtn = e.target.closest('.use-template');
            if (useBtn) {
                const id = useBtn.dataset.id;
                this.showVariablesForm(id);
            }
            
            const deleteBtn = e.target.closest('.delete-template');
            if (deleteBtn) {
                const id = deleteBtn.dataset.id;
                this.deleteTemplate(id);
            }
        });
        
        // Category filter
        const categoryFilter = this.container.querySelector('#categoryFilter');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', (e) => {
                this.filterByCategory(e.target.value);
            });
        }
    }

    showVariablesForm(templateId) {
        const template = this.templateManager.getById(templateId);
        if (!template) return;
        
        this.currentTemplate = template;
        const preview = this.container.querySelector('#templatePreview');
        const variablesDiv = this.container.querySelector('#templateVariables');
        
        if (template.variables.length === 0) {
            this.applyTemplateToForm(template, {});
            return;
        }
        
        variablesDiv.innerHTML = template.variables.map(variable => `
            <div class="form-group">
                <label class="form-label">{${variable}}</label>
                <input type="text" class="form-input template-variable" data-var="${variable}" placeholder="Digite o valor para ${variable}">
            </div>
        `).join('');
        
        preview.style.display = 'block';
        
        // Apply button
        const applyBtn = this.container.querySelector('#applyTemplate');
        applyBtn.onclick = () => {
            const variables = {};
            this.container.querySelectorAll('.template-variable').forEach(input => {
                variables[input.dataset.var] = input.value;
            });
            this.applyTemplateToForm(template, variables);
            preview.style.display = 'none';
        };
        
        // Cancel button
        const cancelBtn = this.container.querySelector('#cancelTemplate');
        cancelBtn.onclick = () => {
            preview.style.display = 'none';
        };
        
        const closeBtn = this.container.querySelector('#closePreview');
        closeBtn.onclick = () => {
            preview.style.display = 'none';
        };
    }

    applyTemplateToForm(template, variables) {
        const result = this.templateManager.applyTemplate(template, variables);
        
        // Update form fields (assuming they exist)
        const subjectField = document.getElementById('subject') || document.getElementById('batchSubject') || document.getElementById('autoSubject');
        const messageField = document.getElementById('message') || document.getElementById('batchMessage') || document.getElementById('autoMessage');
        
        if (subjectField) subjectField.value = result.subject;
        if (messageField) messageField.value = result.body;
        
        window.toastManager.success('Template aplicado com sucesso!');
    }

    deleteTemplate(id) {
        if (!confirm('Deseja realmente excluir este template?')) return;
        
        if (this.templateManager.delete(id)) {
            window.toastManager.success('Template excluído com sucesso!');
            this.render();
            this.attachEvents();
        } else {
            window.toastManager.error('Erro ao excluir template');
        }
    }

    filterByCategory(category) {
        const templates = category ? 
            this.templateManager.getByCategory(category) : 
            this.templateManager.getAll();
        
        const listContainer = this.container.querySelector('#templateList');
        listContainer.innerHTML = this.renderTemplateList(templates);
    }

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
}

// Initialize
window.TemplateManager = TemplateManager;
window.TemplateUI = TemplateUI;
window.templateManager = new TemplateManager();
