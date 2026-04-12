"""
Control del relé DSD TECH SH-UR01A.

Soporta dos modos:
  - "hid"    : protocolo USB-HID estándar (VID 0x16C0 / PID 0x05DF)
  - "serial" : RS-232 over USB (CH340 / CP2102) con protocolo AT

Conexión física al portón BTF:
  Relé COM  →  Terminal 60 del controlador BTF
  Relé NO   →  Terminal 61 del controlador BTF
  (Los terminales 60-61 corresponden al pulsador de apertura)
"""

import time
import threading
import logging
import config

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Comandos HID (protocolo USB-Relay genérico)
# Byte 0:  0xFF = activar, 0xFD = desactivar
# Byte 1:  número de canal (1-based)
# ---------------------------------------------------------------------------
_HID_CMD_ON  = lambda ch: bytes([0xFF, ch, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
_HID_CMD_OFF = lambda ch: bytes([0xFD, ch, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

# ---------------------------------------------------------------------------
# Comandos Serial (protocolo común CH340 relay modules)
# ---------------------------------------------------------------------------
_SERIAL_CMD_ON  = lambda ch: bytes([0xA0, ch, 0x01, 0xA0 + ch + 0x01])
_SERIAL_CMD_OFF = lambda ch: bytes([0xA0, ch, 0x00, 0xA0 + ch])


class RelayController:
    """Encapsula el acceso al relé en modo HID o Serial."""

    def __init__(self):
        self._lock = threading.Lock()
        self._device = None
        self._mode = config.RELAY_MODE
        self._channel = config.RELAY_CHANNEL
        self._connected = False

    # ------------------------------------------------------------------
    # Conexión
    # ------------------------------------------------------------------
    def connect(self) -> bool:
        """Abre la conexión con el relé. Retorna True si tiene éxito."""
        try:
            if self._mode == "hid":
                return self._connect_hid()
            else:
                return self._connect_serial()
        except Exception as exc:
            logger.error("Error al conectar relé: %s", exc)
            return False

    def _connect_hid(self) -> bool:
        import hid  # type: ignore
        dev = hid.device()
        dev.open(config.RELAY_HID_VID, config.RELAY_HID_PID)
        dev.set_nonblocking(1)
        self._device = dev
        self._connected = True
        logger.info(
            "Relé HID conectado — VID=0x%04X PID=0x%04X",
            config.RELAY_HID_VID, config.RELAY_HID_PID,
        )
        return True

    def _connect_serial(self) -> bool:
        import serial  # type: ignore
        port = config.RELAY_SERIAL_PORT
        if not port:
            raise ValueError("RELAY_SERIAL_PORT no configurado en .env")
        ser = serial.Serial(port, config.RELAY_SERIAL_BAUD, timeout=1)
        self._device = ser
        self._connected = True
        logger.info("Relé Serial conectado — puerto %s @ %d baud", port, config.RELAY_SERIAL_BAUD)
        return True

    def disconnect(self):
        if self._device:
            try:
                self._device.close()
            except Exception:
                pass
        self._connected = False
        self._device = None

    @property
    def is_connected(self) -> bool:
        return self._connected

    # ------------------------------------------------------------------
    # Control del relé
    # ------------------------------------------------------------------
    def _write(self, data: bytes):
        if self._mode == "hid":
            # El primer byte del report HID debe ser 0x00 (report ID)
            self._device.write([0x00] + list(data))
        else:
            self._device.write(data)

    def set_relay(self, on: bool):
        """Activa o desactiva el relé."""
        with self._lock:
            if not self._connected:
                raise RuntimeError("Relé no conectado")
            cmd = _HID_CMD_ON(self._channel) if on else _HID_CMD_OFF(self._channel)
            if self._mode == "serial":
                cmd = _SERIAL_CMD_ON(self._channel) if on else _SERIAL_CMD_OFF(self._channel)
            self._write(cmd)
            logger.debug("Relé canal %d → %s", self._channel, "ON" if on else "OFF")

    def pulse(self, seconds: float | None = None):
        """
        Envía un pulso: activa el relé, espera `seconds`, desactiva.
        Seguro para llamar desde cualquier hilo.
        """
        duration = seconds if seconds is not None else config.RELAY_PULSE_SECONDS

        def _do_pulse():
            try:
                self.set_relay(True)
                time.sleep(duration)
                self.set_relay(False)
                logger.info("Pulso de %.1fs enviado al portón", duration)
            except Exception as exc:
                logger.error("Error durante pulso del relé: %s", exc)

        t = threading.Thread(target=_do_pulse, daemon=True)
        t.start()


# Instancia global
relay = RelayController()
