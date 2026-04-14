@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo  Setup - Sistema de Acceso al Porton (Windows)
echo ============================================================
echo.

:: ── Verificar Python ────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo         Descargalo en: https://www.python.org/downloads/
    echo         Marca la opcion "Add Python to PATH" al instalar.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version') do echo [OK] %%v

:: ── Instalar dependencias Python ────────────────────────────────
echo.
echo [1/4] Instalando dependencias Python...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Fallo la instalacion de dependencias.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.

:: ── Instalar mkcert ─────────────────────────────────────────────
echo.
echo [2/4] Instalando mkcert...
where mkcert >nul 2>&1
if errorlevel 1 (
    winget install --id FiloSottile.mkcert -e --silent
    if errorlevel 1 (
        echo [AVISO] No se pudo instalar mkcert con winget.
        echo         Instalalo manualmente: https://github.com/FiloSottile/mkcert/releases
        echo         Luego ejecuta: mkcert -install  y  mkcert localhost 127.0.0.1
        goto :skip_mkcert
    )
    :: Recargar PATH para encontrar mkcert recien instalado
    for /f "tokens=*" %%p in ('where mkcert 2^>nul') do set "MKCERT=%%p"
) else (
    echo [OK] mkcert ya esta instalado.
)

:: ── Registrar CA local y generar certificados ───────────────────
echo.
echo [3/4] Registrando CA local en Windows y generando certificados HTTPS...
mkcert -install
if errorlevel 1 (
    echo [ERROR] Fallo mkcert -install
    pause
    exit /b 1
)

:: Obtener IP local automaticamente
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /R "IPv4.*192\."') do (
    set "LOCAL_IP=%%a"
    set "LOCAL_IP=!LOCAL_IP: =!"
)
if not defined LOCAL_IP (
    for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr "IPv4"') do (
        set "LOCAL_IP=%%a"
        set "LOCAL_IP=!LOCAL_IP: =!"
    )
)
echo [INFO] IP local detectada: !LOCAL_IP!

mkcert localhost 127.0.0.1 !LOCAL_IP!
if errorlevel 1 (
    echo [ERROR] Fallo la generacion del certificado.
    pause
    exit /b 1
)
echo [OK] Certificados generados para localhost, 127.0.0.1 y !LOCAL_IP!

:: Actualizar SERVER_IP en .env si existe
if exist .env (
    powershell -Command "(Get-Content .env) -replace '^SERVER_IP=.*', 'SERVER_IP=!LOCAL_IP!' | Set-Content .env"
    echo [OK] SERVER_IP actualizada en .env: !LOCAL_IP!
)

:skip_mkcert

:: ── Crear .env desde .env.example ───────────────────────────────
echo.
echo [4/4] Creando archivo .env...
if exist .env (
    echo [AVISO] Ya existe un archivo .env — no se sobreescribe.
    echo         Edita .env manualmente si necesitas cambiar algo.
) else (
    copy .env.example .env >nul
    echo [OK] .env creado desde .env.example
)

:: ── Detectar puerto COM del rele ─────────────────────────────────
echo.
echo ── Puertos COM disponibles ──────────────────────────────────
mode | findstr "COM"
echo.
echo Si tu rele DSD TECH SH-UR01A aparece como un puerto COMx arriba,
echo edita .env y cambia RELAY_SERIAL_PORT=COMx
echo Si usa modo HID (USB-HID), deja RELAY_MODE=hid en .env
echo.

:: ── Fin ─────────────────────────────────────────────────────────
echo ============================================================
echo  Setup completado.
echo  Para iniciar el sistema: python main.py
echo ============================================================
echo.
pause
