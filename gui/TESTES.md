# 🧪 Guia de Testes - Melhorias da GUI

## Como Testar as Novas Funcionalidades

### 1. Iniciar o Servidor

```bash
cd gui
python server.py
```

Acesse: http://localhost:5000

---

## ✅ Testes das Funcionalidades

### 📢 Toast Notifications

**Como testar:**
1. Abra a interface
2. Tente fazer login com credenciais inválidas
3. **Resultado esperado:** Toast vermelho de erro (em vez de alert)

4. Faça login com sucesso
5. **Resultado esperado:** Toast verde de sucesso

6. Abra o console (F12) e digite:
```javascript
window.toastManager.success('Teste de sucesso!');
window.toastManager.error('Teste de erro!');
window.toastManager.warning('Teste de aviso!');
window.toastManager.info('Teste de informação!');
```

**✓ Verificações:**
- [ ] Toasts aparecem no canto superior direito
- [ ] Animação suave de entrada
- [ ] Botão X fecha o toast
- [ ] Auto-fecha após alguns segundos
- [ ] Múltiplos toasts empilham corretamente

---

### 📊 Indicador de Progresso

**Como testar:**
1. Vá para "Envio em Lote"
2. Cole vários emails (pelo menos 15):
```
teste1@email.com
teste2@email.com
teste3@email.com
...
```
3. Preencha assunto e mensagem
4. Clique em "Enviar Email(s)"

**✓ Verificações:**
- [ ] Modal de confirmação aparece (>10 emails)
- [ ] Barra de progresso aparece no topo dos logs
- [ ] Mostra contador (ex: 3/15)
- [ ] Mostra percentual (ex: 20%)
- [ ] Mostra tempo estimado
- [ ] Barra avança conforme emails são enviados
- [ ] Fica verde ao completar

**Teste manual do componente:**
```javascript
// Abra o console (F12)
const container = document.getElementById('logContainer');
const progress = new ProgressBar(container);
progress.start(10);

// Simular progresso
let i = 0;
const interval = setInterval(() => {
    i++;
    progress.update(i, `Processando item ${i}...`);
    if (i >= 10) {
        progress.complete('Finalizado!');
        clearInterval(interval);
    }
}, 1000);
```

**✓ Verificações:**
- [ ] Barra de progresso aparece
- [ ] Atualiza a cada segundo
- [ ] Mostra tempo restante
- [ ] Completa em verde

---

### ✉️ Validação de Email em Tempo Real

**Como testar:**
1. Clique no campo "Destinatário" (modo Envio Único)
2. Digite um email inválido: `teste@`
3. **Resultado esperado:** 
   - Ícone X vermelho aparece à direita
   - Borda do campo fica vermelha
   - Mensagem "Email inválido" abaixo

4. Digite um email válido: `teste@email.com`
5. **Resultado esperado:**
   - Ícone ✓ verde aparece
   - Borda do campo fica verde
   - Mensagem "Email válido" abaixo

**✓ Verificações:**
- [ ] Validação acontece enquanto digita (com delay)
- [ ] Ícones aparecem/desaparecem
- [ ] Cores mudam (verde/vermelho)
- [ ] Mensagens são exibidas

---

### 🔒 Indicador de Força de Senha

**Como testar:**
1. Clique no campo "Senha"
2. Digite senhas diferentes:
   - `123` → Fraca (vermelho)
   - `senha123` → Média (laranja)
   - `Senha123` → Boa (azul)
   - `Senha123!@#` → Forte (verde)

**✓ Verificações:**
- [ ] Barra de força aparece abaixo do campo
- [ ] Cor muda conforme a senha
- [ ] Label muda (Fraca/Média/Boa/Forte)
- [ ] Barra cresce/diminui

---

### 👁️ Preview de Email

**Como testar:**
1. Vá para "Envio Único"
2. Preencha:
   - Destinatário: `teste@email.com`
   - Assunto: `Teste de Preview`
   - Mensagem: `Esta é uma mensagem de teste`
3. Clique em "Pré-visualizar"

**✓ Verificações:**
- [ ] Modal de preview abre
- [ ] Mostra destinatário
- [ ] Mostra assunto
- [ ] Mostra mensagem formatada
- [ ] Mostra anexos (se houver)
- [ ] Botão "Fechar" funciona
- [ ] Botão "Enviar Teste para Mim" funciona
- [ ] Botão "Confirmar e Enviar" funciona
- [ ] ESC fecha o modal
- [ ] Clicar fora fecha o modal

**Teste de envio de teste:**
1. No preview, clique em "Enviar Teste para Mim"
2. Digite um email válido
3. **Resultado esperado:**
   - Email enviado com prefixo [TESTE]
   - Toast de sucesso aparece

---

### 📝 Sistema de Templates

**Como testar:**
1. Clique no modo "Templates"
2. **Resultado esperado:** Seção de templates aparece

**Visualizar templates padrão:**
**✓ Verificações:**
- [ ] 3 templates aparecem (Boas-vindas, Follow-up, Fatura)
- [ ] Cada template mostra nome, categoria, assunto
- [ ] Botões de ação (usar, editar, deletar) aparecem

**Usar um template:**
1. Clique no ícone ✓ (usar) do template "Boas-vindas"
2. **Resultado esperado:** Modal aparece pedindo valores das variáveis
3. Preencha:
   - {nome}: João
   - {empresa}: Acme Corp
4. Clique em "Aplicar Template"
5. Volte para "Envio Único"

**✓ Verificações:**
- [ ] Assunto foi preenchido com template
- [ ] Mensagem foi preenchida com template
- [ ] Variáveis foram substituídas pelos valores

**Criar novo template:**
1. No modo Templates, clique em "Novo Template"
2. Preencha:
   - Nome: Teste
   - Assunto: Olá {nome}
   - Mensagem: Esta é uma mensagem para {nome}
   - Categoria: personalizado
3. Salve

**✓ Verificações:**
- [ ] Template aparece na lista
- [ ] Persiste após reload (F5)
- [ ] Pode ser usado normalmente

**Filtrar templates:**
1. Use o dropdown "Todas as categorias"
2. Selecione uma categoria

**✓ Verificações:**
- [ ] Lista filtra corretamente
- [ ] "Todas" mostra todos

---

### ⚠️ Confirmação de Envio em Massa

**Como testar:**
1. Vá para "Envio em Lote"
2. Cole 15+ emails
3. Preencha assunto e mensagem
4. Clique em "Enviar Email(s)"

**✓ Verificações:**
- [ ] Modal de confirmação aparece
- [ ] Mostra quantidade de emails
- [ ] Ícone de aviso (⚠️) aparece
- [ ] Botão "Cancelar" funciona
- [ ] Botão "Confirmar" prossegue com envio

**Com menos de 10 emails:**
1. Cole apenas 5 emails
2. Clique em "Enviar Email(s)"

**✓ Verificações:**
- [ ] Modal NÃO aparece
- [ ] Envia diretamente

---

## 🔍 Testes de Console

Abra o console (F12) e verifique:

```javascript
// Verificar se componentes carregaram
console.log(window.toastManager); // ToastManager
console.log(window.ProgressBar); // Class
console.log(window.Validator); // Class
console.log(window.EmailPreview); // Class
console.log(window.templateManager); // TemplateManager
console.log(window.templateUI); // TemplateUI

// Deve aparecer:
// ✅ Componentes de melhorias carregados com sucesso!
```

---

## 📱 Teste Responsivo

**Como testar:**
1. Pressione F12 para abrir DevTools
2. Clique no ícone de device toolbar (ou Ctrl+Shift+M)
3. Selecione "iPhone 12 Pro" ou similar
4. Teste todas as funcionalidades acima

**✓ Verificações:**
- [ ] Toasts aparecem corretamente
- [ ] Modals são responsivos
- [ ] Botões são clicáveis
- [ ] Textos legíveis
- [ ] Sem overflow horizontal

---

## 🎨 Teste Visual

**Verificar aparência:**
- [ ] Toasts têm cores distintas (verde, vermelho, amarelo, azul)
- [ ] Animações são suaves
- [ ] Ícones aparecem corretamente
- [ ] Fontes estão consistentes
- [ ] Espaçamento está correto
- [ ] Dark theme está mantido

---

## 🐛 Testes de Erro

**Teste de erros comuns:**

1. **Email inválido:**
   - Digite email sem @ → Deve invalidar
   - Digite email sem domínio → Deve invalidar

2. **Campos vazios:**
   - Tente preview sem preencher campos → Deve avisar

3. **Múltiplos toasts:**
   - Dispare 10 toasts rapidamente → Devem empilhar sem sobrepor

4. **Template com variáveis não preenchidas:**
   - Use template sem preencher valores → Variáveis ficam como {nome}

---

## ✅ Checklist Final

### Funcionalidades Principais:
- [ ] Toasts funcionam
- [ ] Progress bars funcionam
- [ ] Validação de email funciona
- [ ] Indicador de senha funciona
- [ ] Preview funciona
- [ ] Templates funcionam
- [ ] Confirmação em massa funciona

### Integrações:
- [ ] Substituição de alerts funciona
- [ ] Envio em lote mostra progresso
- [ ] Preview integrado ao botão existente
- [ ] Templates integrados aos formulários

### Performance:
- [ ] Sem erros no console
- [ ] Animações suaves (60fps)
- [ ] Sem travamentos
- [ ] Responsivo em mobile

---

## 🎉 Resultado Esperado

Após todos os testes, a interface deve:
- ✅ Ter feedback visual profissional
- ✅ Validar inputs em tempo real
- ✅ Mostrar progresso de envios
- ✅ Permitir preview e teste
- ✅ Gerenciar templates facilmente
- ✅ Confirmar ações críticas
- ✅ Ser 100% funcional

**Se todos os testes passarem, as melhorias foram implementadas com sucesso! 🎊**
