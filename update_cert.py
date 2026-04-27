"""
Actualiza el certificado HTTPS y la IP local en .env.

Uso:
    python update_cert.py

Qué hace:
  1. Detecta la IP local actual del equipo
  2. Regenera el certificado mkcert con esa IP
  3. Actualiza SERVER_IP, SSL_CERTFILE y SSL_KEYFILE en .env
"""

import os
import re
import socket
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
ENV_FILE = BASE_DIR / ".env"


# ── Detectar IP local ──────────────────────────────────────────────────────
def get_local_ip() -> str:
    """Retorna la IP local activa (la que sale hacia internet/LAN)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# ── Regenerar certificado con mkcert ─────────────────────────────────────
def regenerate_cert(ip: str) -> tuple[str, str]:
    """
    Ejecuta mkcert y retorna (certfile, keyfile).
    Genera: localhost+2.pem / localhost+2-key.pem
    """
    hosts = ["localhost", "127.0.0.1", ip]
    print(f"Generando certificado para: {', '.join(hosts)}")

    result = subprocess.run(
        ["mkcert"] + hosts,
        cwd=str(BASE_DIR),
        capture_output=True,
        text=True,
    )

    output = (result.stdout + result.stderr).strip()
    if result.returncode != 0:
        print("ERROR al ejecutar mkcert:")
        print(output)
        sys.exit(1)

    print(output)

    # mkcert nombra el archivo según el número de hosts extras
    extra = len(hosts) - 1          # hosts extra después del primero
    certfile = f"localhost+{extra}.pem"
    keyfile  = f"localhost+{extra}-key.pem"
    return certfile, keyfile


# ── Actualizar .env ───────────────────────────────────────────────────────
def update_env(ip: str, certfile: str, keyfile: str):
    """Actualiza SERVER_IP, SSL_CERTFILE y SSL_KEYFILE en .env."""
    if not ENV_FILE.exists():
        print(f"AVISO: no se encontró {ENV_FILE}. Copia .env.example a .env primero.")
        return

    content = ENV_FILE.read_text(encoding="utf-8")

    replacements = {
        r"^SERVER_IP=.*":    f"SERVER_IP={ip}",
        r"^SSL_CERTFILE=.*": f"SSL_CERTFILE={certfile}",
        r"^SSL_KEYFILE=.*":  f"SSL_KEYFILE={keyfile}",
    }

    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    ENV_FILE.write_text(content, encoding="utf-8")
    print(f".env actualizado:")
    print(f"  SERVER_IP   = {ip}")
    print(f"  SSL_CERTFILE = {certfile}")
    print(f"  SSL_KEYFILE  = {keyfile}")


# ── Main ──────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print(" Actualización de certificado e IP local")
    print("=" * 55)

    ip = get_local_ip()
    print(f"\nIP local detectada: {ip}")

    certfile, keyfile = regenerate_cert(ip)
    update_env(ip, certfile, keyfile)

    print("\nListo. Reinicia main.py para aplicar los cambios.")
    print("=" * 55)


if __name__ == "__main__":
    main()
