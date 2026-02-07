@echo off
chcp 65001 > nul
echo.
echo ============================================================
echo   ORGANIZANDO PROJETO EM PASTAS
echo ============================================================
echo.
python organizar.py
echo.
echo ============================================================
echo   ORGANIZACAO CONCLUIDA!
echo ============================================================
echo.
echo Pressione qualquer tecla para ver a nova estrutura...
pause > nul
dir /b
echo.
pause
