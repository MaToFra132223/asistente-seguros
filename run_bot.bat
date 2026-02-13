@echo off
title Mirabet Seguros Bot (IA)
echo ==========================================
echo    INICIANDO EL ASISTENTE INTELIGENTE
echo ==========================================
echo.
echo  1. Asegurate de haber configurado 'configuracion.py'
echo  2. Asegurate de tener tu API Key en el archivo .env
echo.
echo Iniciando...
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
python main.py
echo.
echo El bot se ha detenido.
pause
