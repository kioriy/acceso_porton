"""
Script de prueba — simula el POST que haría la app QR.
Úsalo sin necesidad de la app real para validar el UI y el relé.

Lee SERVER_PORT, API_SECRET, SSL_CERTFILE y SSL_KEYFILE del .env automáticamente.

Uso:
    python test_qr_payload.py [autorizado|denegado]
"""

import os
import ssl
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime

# --- leer .env manualmente (sin dependencias extra) -------------------------
def _load_env(path=".env"):
    env = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                env[key.strip()] = val.strip()
    except FileNotFoundError:
        pass
    return env

_env = _load_env()

_port      = int(_env.get("SERVER_PORT", os.getenv("SERVER_PORT", "8765")))
_certfile  = _env.get("SSL_CERTFILE",  os.getenv("SSL_CERTFILE", ""))
_keyfile   = _env.get("SSL_KEYFILE",   os.getenv("SSL_KEYFILE",  ""))
_api_secret = _env.get("API_SECRET",  os.getenv("API_SECRET",   ""))

_scheme = "https" if (_certfile and _keyfile) else "http"
HOST = f"{_scheme}://localhost:{_port}"

PAYLOAD_AUTORIZADO = {
    "status": "autorizado",
    "residente": "Hugo Rafael Hernandez Llamas",
    "casa": "387",
    "visitante": "Javier Hernandez",
    "tipo_acceso": "FAMILIAR",
    "forma": "Vehiculo",
    "vigencia": datetime.now().strftime("%d %b %Y, %I:%M %p"),
    "acceso": datetime.now().strftime("%d %b %Y, %I:%M %p"),
}

PAYLOAD_DENEGADO = {
    "status": "denegado",
    "residente": "Sin autorización",
    "casa": "000",
    "visitante": "Desconocido",
    "tipo_acceso": "—",
    "forma": "Vehiculo",
    "vigencia": "Vencido",
    "acceso": datetime.now().strftime("%d %b %Y, %I:%M %p"),
}


def send(payload: dict):
    data    = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    if _api_secret:
        headers["X-Api-Key"] = _api_secret

    req = urllib.request.Request(
        f"{HOST}/acceso",
        data=data,
        headers=headers,
        method="POST",
    )

    # HTTPS: usar la CA de mkcert para validar el certificado local
    ctx = None
    if _scheme == "https":
        import subprocess
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        try:
            caroot = subprocess.check_output(
                ["mkcert", "-CAROOT"], text=True
            ).strip()
            ca_pem = os.path.join(caroot, "rootCA.pem")
            if os.path.exists(ca_pem):
                ctx.load_verify_locations(ca_pem)
            else:
                raise FileNotFoundError(ca_pem)
        except Exception:
            ctx.check_hostname = False
            ctx.verify_mode    = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
            body = json.loads(resp.read())
            print("Respuesta:", body)
    except urllib.error.URLError as e:
        print("Error — ¿está corriendo main.py?:", e)


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "autorizado"
    payload = PAYLOAD_AUTORIZADO if modo == "autorizado" else PAYLOAD_DENEGADO
    print(f"Enviando payload '{modo}'...")
    send(payload)
