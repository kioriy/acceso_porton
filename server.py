"""
Servidor HTTP (FastAPI + Uvicorn) que recibe el JSON del escaneo QR
desde la PWA y emite una señal Qt al UI principal.

Payload esperado (POST /acceso):
{
  "status":       "autorizado" | "denegado",
  "residente":    "Hugo Rafael Hernandez Llamas",
  "casa":         "387",
  "visitante":    "Javier Hernandez",
  "tipo_acceso":  "FAMILIAR",
  "forma":        "Vehiculo",
  "vigencia":     "08 Apr 2026, 06:34 PM",
  "acceso":       "08 Apr 2026, 06:34 PM"   // opcional
}
"""

import logging
import threading
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config
from relay_controller import relay

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------
class AccesoPayload(BaseModel):
    status: str                         # "autorizado" | "denegado"
    residente: str
    casa: str
    visitante: Optional[str] = ""
    tipo_acceso: Optional[str] = ""
    forma: Optional[str] = ""
    vigencia: Optional[str] = ""
    acceso: Optional[str] = ""


# ---------------------------------------------------------------------------
# Callback — se inyecta desde main.py para notificar al UI Qt
# ---------------------------------------------------------------------------
_ui_callback = None  # Callable[[AccesoPayload], None]


def set_ui_callback(fn):
    global _ui_callback
    _ui_callback = fn


# ---------------------------------------------------------------------------
# App FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(title="Acceso Portón", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


def _check_api_key(x_api_key: Optional[str]):
    if config.API_SECRET and x_api_key != config.API_SECRET:
        raise HTTPException(status_code=401, detail="API key inválida")


@app.get("/health")
def health():
    return {"ok": True, "relay_connected": relay.is_connected}


@app.post("/acceso")
async def registrar_acceso(
    payload: AccesoPayload,
    x_api_key: Optional[str] = Header(default=None),
):
    _check_api_key(x_api_key)

    logger.info(
        "Acceso recibido — status=%s casa=%s residente=%s",
        payload.status, payload.casa, payload.residente,
    )

    # Notificar UI (hilo principal Qt)
    if _ui_callback:
        _ui_callback(payload)

    # Abrir portón solo si está autorizado
    if payload.status.lower() == "autorizado":
        if relay.is_connected:
            relay.pulse()
        else:
            logger.warning("Relé no conectado — portón no abierto")

    return {"ok": True, "portón_abierto": payload.status.lower() == "autorizado"}


# ---------------------------------------------------------------------------
# Arrancar en hilo daemon
# ---------------------------------------------------------------------------
def start_server():
    """Inicia uvicorn en un hilo de fondo (HTTP o HTTPS según config)."""
    use_tls = bool(config.SSL_CERTFILE and config.SSL_KEYFILE)

    def _run():
        kwargs = dict(
            host=config.SERVER_HOST,
            port=config.SERVER_PORT,
            log_level="warning",
        )
        if use_tls:
            kwargs["ssl_certfile"] = config.SSL_CERTFILE
            kwargs["ssl_keyfile"]  = config.SSL_KEYFILE

        uvicorn.run(app, **kwargs)

    t = threading.Thread(target=_run, daemon=True, name="uvicorn")
    t.start()
    scheme = "https" if use_tls else "http"
    logger.info("Servidor listo: %s://%s:%d", scheme, config.SERVER_HOST, config.SERVER_PORT)
