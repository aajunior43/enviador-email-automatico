@echo off
chcp 65001 > nul
title Enviador de Email Automático - Interface Web

echo ================================================================================
echo   ENVIADOR DE EMAIL AUTOMÁTICO - INTERFACE WEB
echo ================================================================================
echo.

REM Verificar se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado!
    echo    Por favor, instale o Python 3.7+ antes de continuar.
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

REM Verificar se as dependências estão instaladas
echo 📦 Verificando dependências...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Flask não encontrado. Instalando dependências...
    echo.
    pip install flask flask-cors
    echo.
)

echo ✅ Dependências OK
echo.

REM Iniciar servidor
echo 🚀 Iniciando servidor web...
echo.
cd /d "%~dp0"
python server.py

pause
