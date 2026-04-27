"""
Configuración central del sistema de acceso al portón.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Servidor HTTP ---
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8765"))
SERVER_IP   = os.getenv("SERVER_IP", "127.0.0.1")  # IP local del equipo (para la PWA)
API_SECRET  = os.getenv("API_SECRET", "")   # Si se define, se valida en el header X-Api-Key

# TLS — dejar vacío para HTTP plano, o apuntar a los archivos generados por mkcert
SSL_CERTFILE = os.getenv("SSL_CERTFILE", "")   # ej: localhost+2.pem
SSL_KEYFILE  = os.getenv("SSL_KEYFILE",  "")   # ej: localhost+2-key.pem

# --- Relé DSD TECH SH-UR01A ---
# Modo: "hid" (USB-HID) o "serial" (CH340/CP2102)
RELAY_MODE = os.getenv("RELAY_MODE", "hid")

# HID — VID/PID del SH-UR01A (protocolo USB-relay estándar)
RELAY_HID_VID = int(os.getenv("RELAY_HID_VID", "0x16C0"), 16)
RELAY_HID_PID = int(os.getenv("RELAY_HID_PID", "0x05DF"), 16)

# Serial — puerto y velocidad (ej. /dev/tty.usbserial-XXX en macOS)
RELAY_SERIAL_PORT = os.getenv("RELAY_SERIAL_PORT", "")
RELAY_SERIAL_BAUD = int(os.getenv("RELAY_SERIAL_BAUD", "9600"))

# Duración del pulso de apertura en segundos
RELAY_PULSE_SECONDS = float(os.getenv("RELAY_PULSE_SECONDS", "1.0"))

# Número de canal del relé (1-based; SH-UR01A tiene 1 canal)
RELAY_CHANNEL = int(os.getenv("RELAY_CHANNEL", "1"))
