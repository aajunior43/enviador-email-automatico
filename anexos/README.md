# Pasta de Anexos

Coloque aqui os arquivos que deseja anexar aos emails.

## 💡 Nomeie os arquivos com o email do destinatário

### Para um único arquivo por destinatário:
```
anexos/
├── cliente1@empresa.com.pdf
├── cliente2@empresa.com.pdf
└── cliente3@empresa.com.pdf
```

### Para múltiplos arquivos para o mesmo destinatário:
Use sufixos numéricos (`-1`, `-2`, etc):
```
anexos/
├── cliente@empresa.com.pdf
├── cliente@empresa.com-1.xlsx
├── cliente@empresa.com-2.docx
└── fornecedor@empresa.com.pdf
```

**Resultado:** O cliente@empresa.com receberá **1 email com 3 anexos** (pdf, xlsx, docx)!

O bot agrupa automaticamente todos os arquivos do mesmo destinatário em um único email! 🎯
