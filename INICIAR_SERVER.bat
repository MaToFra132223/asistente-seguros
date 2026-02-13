@echo off
title Servidor Webhook - Mirabet Seguros
echo ==========================================
echo    INICIANDO SERVIDOR WEBHOOK (API)
echo ==========================================
echo.
echo  1. Asegurate de tener corriendo ngrok en otra ventana
echo     (Comando: ngrok http 5000)
echo.
echo  2. Configura la URL de ngrok en Meta Developers
echo.
echo Iniciando servidor Flask...
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
venv\Scripts\python.exe webhook_server.py
echo.
echo El servidor se ha detenido.
pause
