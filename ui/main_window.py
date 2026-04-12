"""
Ventana principal del sistema de acceso al portón.
Recibe eventos desde el servidor HTTP via señales Qt y actualiza el UI.
"""

import logging

from PySide6.QtCore import Qt, Signal, QObject, QTimer, Slot
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from PySide6.QtGui import QFont

from .access_widget import AccessWidget
from .idle_widget import IdleWidget

logger = logging.getLogger(__name__)


class ServerBridge(QObject):
    """
    Puente entre el hilo del servidor HTTP y el hilo Qt.
    Emite señales seguras para el UI.
    """
    acceso_recibido = Signal(object)  # dict con datos de acceso


# Creación diferida — se instancia DESPUÉS de QApplication
_bridge_instance = None


def get_bridge() -> ServerBridge:
    """Devuelve (y crea si es necesario) el singleton del bridge."""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = ServerBridge()
        logger.debug("ServerBridge creado — thread: %s", _bridge_instance.thread())
    return _bridge_instance


class MainWindow(QMainWindow):
    DISPLAY_SECONDS = 8  # Segundos antes de volver al estado idle

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control de Acceso — Portón")
        self.setMinimumSize(480, 780)

        # Stack: 0=idle, 1=resultado acceso
        self._stack = QStackedWidget()
        self._idle = IdleWidget()
        self._access = AccessWidget()

        self._stack.addWidget(self._idle)   # índice 0
        self._stack.addWidget(self._access) # índice 1

        self.setCentralWidget(self._stack)

        # Timer para volver a idle
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._show_idle)

        # Conectar señal del bridge con QueuedConnection explícito
        bridge = get_bridge()
        bridge.acceso_recibido.connect(self._on_acceso, Qt.QueuedConnection)
        logger.info("Señal acceso_recibido conectada (QueuedConnection)")

        self._show_idle()

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------
    @Slot(object)
    def _on_acceso(self, payload):
        logger.info("_on_acceso activado — payload recibido: %s", type(payload))
        try:
            self._access.update_data(payload)
            self._stack.setCurrentIndex(1)
            self._timer.start(self.DISPLAY_SECONDS * 1000)
            logger.info("UI actualizado — mostrando resultado de acceso")
        except Exception:
            logger.exception("Error al actualizar UI con payload")

    def _show_idle(self):
        self._stack.setCurrentIndex(0)
