#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para organizar arquivos do projeto em pastas"""

import os
import shutil

def criar_estrutura():
    """Cria a estrutura de pastas"""
    pastas = [
        'docs',
        'scripts',
        'data',
        'data/anexos',
        'data/destinatarios',
        'data/enviados',
        'data/triagem'
    ]
    
    for pasta in pastas:
        os.makedirs(pasta, exist_ok=True)
        print(f"✅ Pasta criada: {pasta}")

def mover_arquivos():
    """Move arquivos para pastas organizadas"""
    
    # Mover documentos para docs/
    docs = [
        'README.md',
        'BEM-VINDO.md',
        'ESTRUTURA.md',
        'NAVEGACAO.md',
        'GUI_UPDATE_v2.0.md',
        'LOGGING_GUIDE.md',
        'CORRECAO_MOVIMENTACAO.md',
        'Relatorio_20260205.pdf'
    ]
    
    for doc in docs:
        if os.path.exists(doc):
            shutil.move(doc, f'docs/{doc}')
            print(f"📄 Movido: {doc} → docs/")
    
    # Mover scripts para scripts/
    scripts_files = [
        'main.py',
        'executar.bat'
    ]
    
    for script in scripts_files:
        if os.path.exists(script):
            shutil.move(script, f'scripts/{script}')
            print(f"🔧 Movido: {script} → scripts/")
    
    # Mover dados para data/
    dados = ['anexos', 'destinatarios', 'enviados', 'triagem']
    
    for dado in dados:
        if os.path.exists(dado) and os.path.isdir(dado):
            # Mover conteúdo
            dest = f'data/{dado}'
            if os.path.exists(dest):
                # Mover arquivos dentro
                for item in os.listdir(dado):
                    src = os.path.join(dado, item)
                    dst = os.path.join(dest, item)
                    if os.path.exists(dst):
                        if os.path.isdir(dst):
                            shutil.rmtree(dst)
                        else:
                            os.remove(dst)
                    shutil.move(src, dst)
                os.rmdir(dado)
            else:
                shutil.move(dado, dest)
            print(f"📁 Movido: {dado} → data/")

def atualizar_paths():
    """Atualiza paths nos arquivos"""
    
    # Atualizar executar.bat
    bat_path = 'scripts/executar.bat'
    if os.path.exists(bat_path):
        with open(bat_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Atualizar paths
        content = content.replace('python main.py', 'python scripts\\main.py')
        
        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"🔄 Atualizado: {bat_path}")
    
    # Atualizar main.py
    main_path = 'scripts/main.py'
    if os.path.exists(main_path):
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Atualizar paths relativos
        replacements = {
            "'anexos'": "'../data/anexos'",
            '"anexos"': '"../data/anexos"',
            "'destinatarios'": "'../data/destinatarios'",
            '"destinatarios"': '"../data/destinatarios"',
            "'enviados'": "'../data/enviados'",
            '"enviados"': '"../data/enviados"',
            "'triagem'": "'../data/triagem'",
            '"triagem"': '"../data/triagem"',
            "'config'": "'../config'",
            '"config"': '"../config"',
            "'logs'": "'../logs'",
            '"logs"': '"../logs"'
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        with open(main_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"🔄 Atualizado: {main_path}")

def criar_novo_executar():
    """Cria novo executar.bat na raiz"""
    content = """@echo off
chcp 65001 > nul
cd scripts
python main.py
pause
"""
    with open('executar.bat', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Criado: executar.bat (na raiz)")

def main():
    print("=" * 60)
    print("🗂️  ORGANIZANDO PROJETO")
    print("=" * 60)
    print()
    
    print("📁 ETAPA 1: Criando estrutura de pastas...")
    criar_estrutura()
    print()
    
    print("📦 ETAPA 2: Movendo arquivos...")
    mover_arquivos()
    print()
    
    print("🔄 ETAPA 3: Atualizando paths nos arquivos...")
    atualizar_paths()
    print()
    
    print("✨ ETAPA 4: Criando executar.bat na raiz...")
    criar_novo_executar()
    print()
    
    print("=" * 60)
    print("✅ ORGANIZAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print()
    print("📂 Nova estrutura:")
    print("   ├── docs/          (8 documentos)")
    print("   ├── scripts/       (main.py, executar.bat)")
    print("   ├── data/          (anexos, destinatarios, enviados, triagem)")
    print("   ├── gui/           (interface web)")
    print("   ├── config/        (configurações)")
    print("   ├── logs/          (arquivos de log)")
    print("   └── executar.bat   (executa o sistema)")
    print()

if __name__ == '__main__':
    main()
