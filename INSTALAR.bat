@echo off
title Instalador Asistente Seguros IA
echo ==========================================
echo    INSTALANDO COMPONENTES DEL BOT...
echo ==========================================
echo.

:: 1. Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo Por favor instala Python desde https://www.python.org/downloads/
    echo y asegurate de marcar "Add Python to PATH" durante la instalación.
    pause
    exit /b
)

echo [OK] Python detectado.
echo.

:: 2. Instalar Librerias (pip)
echo Instalando librerias necesarias...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Fallo al instalar las librerias. Revisa tu conexion a internet.
    pause
    exit /b
)

echo [OK] Librerias instaladas.
echo.

:: 3. Instalar Navegadores (Playwright)
echo Instalando navegadores para el bot (Playwright)...
playwright install chromium

if %errorlevel% neq 0 (
    echo [ERROR] Fallo al instalar los navegadores.
    pause
    exit /b
)

echo [OK] Todo listo!
echo.
echo ==========================================
echo    INSTALACION COMPLETADA EXITOSAMENTE
echo ==========================================
echo.
echo Ahora configura 'configuracion.py' y .env con tu API Key.
echo Luego ejecuta 'INICIAR_BOT.bat'.
pause
