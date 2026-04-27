"""
Punto de entrada del sistema de control de acceso al portón.

Arranca:
  1. Servidor HTTP FastAPI en hilo daemon (puerto 8765)
  2. Intenta conectar el relé USB DSD TECH SH-UR01A
  3. Abre la interfaz gráfica PySide6

La app QR (PWA PHP+Ionic) hace POST a:
  http://<IP_MAQUINA>:8765/acceso
"""

import sys
import asyncio
import logging
import signal

# Evita el error WinError 10054 de asyncio en Windows
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

import config
import server as srv
from relay_controller import relay
from ui.main_window import MainWindow, get_bridge

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Se asigna después de crear QApplication
_bridge = None


def _ui_callback(payload):
    """Llamado desde el hilo del servidor — emite señal segura a Qt."""
    logger.info("_ui_callback llamado — emitiendo señal acceso_recibido")
    try:
        _bridge.acceso_recibido.emit(payload)
    except Exception:
        logger.exception("Error al emitir señal acceso_recibido")


def main():
    # Permitir cierre con Ctrl+C en terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # 1. Conectar relé
    connected = relay.connect()
    if not connected:
        logger.warning(
            "No se pudo conectar el relé. "
            "El sistema funcionará sin abrir el portón físico."
        )

    # 2. Iniciar UI Qt (ANTES del bridge para que QObject tenga thread affinity correcto)
    app = QApplication(sys.argv)
    app.setApplicationName("Acceso Portón")
    # Qt 6 ya maneja High DPI de forma automática
    # app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    # 3. Crear bridge DESPUÉS de QApplication
    global _bridge
    _bridge = get_bridge()
    logger.info("Bridge creado en hilo principal")

    # 4. Iniciar servidor HTTP
    srv.set_ui_callback(_ui_callback)
    srv.start_server()
    logger.info(
        "Servidor listo. Endpoint: http://%s:%d/acceso",
        config.SERVER_HOST, config.SERVER_PORT,
    )

    # 5. Crear y mostrar ventana
    window = MainWindow()
    window.show()

    exit_code = app.exec()

    # Limpieza
    relay.disconnect()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
