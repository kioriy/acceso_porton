"""
Widget de resultado de acceso — fiel al diseño de la app QR.
Muestra: header verde/rojo, residente, #casa, visitante, tipo, forma, vigencia.
"""

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QGraphicsDropShadowEffect, QSizePolicy,
)
from PySide6.QtGui import QFont, QColor


# ---------------------------------------------------------------------------
# Paleta de colores
# ---------------------------------------------------------------------------
COLOR_GRANTED   = "#2E7D32"   # verde oscuro
COLOR_DENIED    = "#C62828"   # rojo oscuro
COLOR_BADGE_OK  = "#43A047"
COLOR_BADGE_ERR = "#E53935"
COLOR_BG        = "#F4F6FA"
COLOR_CARD_BG   = "#FFFFFF"
COLOR_DARK_BLUE = "#1A237E"
COLOR_GREY_LBL  = "#78909C"
COLOR_BODY_TXT  = "#263238"


def _label(text="", font_size=13, bold=False, color=COLOR_BODY_TXT, align=Qt.AlignLeft) -> QLabel:
    lbl = QLabel(text)
    lbl.setAlignment(align)
    weight = QFont.Bold if bold else QFont.Normal
    lbl.setFont(QFont("Arial", font_size, weight))
    lbl.setStyleSheet(f"color: {color}; background: transparent;")
    lbl.setWordWrap(True)
    return lbl


def _separator() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet("color: #E0E0E0;")
    return line


class InfoRow(QWidget):
    """Fila ícono + etiqueta pequeña + valor."""

    def __init__(self, icon: str, field: str, value: str = "", parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 4, 0, 4)
        row.setSpacing(12)

        self._icon_lbl = QLabel(icon)
        self._icon_lbl.setFont(QFont("Arial", 18))
        self._icon_lbl.setFixedWidth(32)
        self._icon_lbl.setStyleSheet("background: transparent;")
        row.addWidget(self._icon_lbl)

        texts = QVBoxLayout()
        texts.setSpacing(0)

        self._field_lbl = _label(field, 10, color=COLOR_GREY_LBL)
        self._field_lbl.setContentsMargins(0, 0, 0, 0)
        texts.addWidget(self._field_lbl)

        self._value_lbl = _label(value, 14, bold=True)
        self._value_lbl.setContentsMargins(0, 0, 0, 0)
        texts.addWidget(self._value_lbl)

        row.addLayout(texts)
        row.addStretch()

    def set_value(self, value: str):
        self._value_lbl.setText(value)

    def set_field(self, field: str):
        self._field_lbl.setText(field)


class TwoColumnRow(QWidget):
    """Dos InfoRow lado a lado."""

    def __init__(self, icon1, field1, val1, icon2, field2, val2, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        self._left  = InfoRow(icon1, field1, val1)
        self._right = InfoRow(icon2, field2, val2)

        row.addWidget(self._left,  1)
        row.addWidget(self._right, 1)

    def set_values(self, val_left: str, val_right: str):
        self._left.set_value(val_left)
        self._right.set_value(val_right)


# ---------------------------------------------------------------------------
# Widget principal
# ---------------------------------------------------------------------------
class AccessWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLOR_BG};")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── HEADER ──────────────────────────────────────────────────────
        self._header = QWidget()
        self._header.setFixedHeight(220)
        header_layout = QVBoxLayout(self._header)
        header_layout.setAlignment(Qt.AlignCenter)
        header_layout.setSpacing(8)

        # Badge de estado
        self._badge = QWidget()
        self._badge.setFixedSize(220, 32)
        self._badge.setStyleSheet(
            f"background: rgba(255,255,255,0.25); border-radius: 16px;"
        )
        badge_row = QHBoxLayout(self._badge)
        badge_row.setContentsMargins(10, 0, 10, 0)
        badge_row.setSpacing(6)

        self._badge_icon = QLabel("✓")
        self._badge_icon.setFont(QFont("Arial", 13, QFont.Bold))
        self._badge_icon.setStyleSheet("color: white; background: transparent;")

        self._badge_text = QLabel("ACCESO AUTORIZADO")
        self._badge_text.setFont(QFont("Arial", 11, QFont.Bold))
        self._badge_text.setStyleSheet(
            "color: white; background: transparent; letter-spacing: 1px;"
        )

        badge_row.addStretch()
        badge_row.addWidget(self._badge_icon)
        badge_row.addWidget(self._badge_text)
        badge_row.addStretch()
        header_layout.addWidget(self._badge, alignment=Qt.AlignCenter)

        # Título principal
        self._title = _label("Acceso Concedido", 32, bold=True, color="white", align=Qt.AlignCenter)
        header_layout.addWidget(self._title)

        # Sub-líneas residente
        self._sub1 = _label("Residente Responsable", 13, color="rgba(255,255,255,0.8)", align=Qt.AlignCenter)
        self._sub2 = _label("", 15, bold=True, color="white", align=Qt.AlignCenter)
        header_layout.addWidget(self._sub1)
        header_layout.addWidget(self._sub2)

        root.addWidget(self._header)

        # ── CUERPO (tarjeta blanca redondeada) ──────────────────────────
        card_container = QWidget()
        card_container.setStyleSheet("background: transparent;")
        card_v = QVBoxLayout(card_container)
        card_v.setContentsMargins(20, 0, 20, 20)
        card_v.setSpacing(12)

        # Tarjeta #Casa
        self._casa_card = QFrame()
        self._casa_card.setStyleSheet(
            f"background: {COLOR_CARD_BG}; border-radius: 16px; border: 1px solid #E0E0E0;"
        )
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self._casa_card.setGraphicsEffect(shadow)

        casa_layout = QVBoxLayout(self._casa_card)
        casa_layout.setContentsMargins(16, 16, 16, 16)
        casa_layout.setSpacing(4)

        casa_top = _label("CASA", 11, color=COLOR_GREY_LBL, align=Qt.AlignCenter)
        casa_top.setStyleSheet(
            f"color: {COLOR_GREY_LBL}; background: transparent; letter-spacing: 2px;"
        )
        self._casa_num = _label("#---", 42, bold=True, color=COLOR_DARK_BLUE, align=Qt.AlignCenter)

        casa_layout.addWidget(casa_top)
        casa_layout.addWidget(self._casa_num)
        card_v.addWidget(self._casa_card)

        # Filas de info
        info_card = QFrame()
        info_card.setStyleSheet(
            f"background: {COLOR_CARD_BG}; border-radius: 16px; border: 1px solid #E0E0E0;"
        )
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(16)
        shadow2.setColor(QColor(0, 0, 0, 25))
        shadow2.setOffset(0, 4)
        info_card.setGraphicsEffect(shadow2)

        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(20, 16, 20, 16)
        info_layout.setSpacing(8)

        self._row_visitante  = InfoRow("👤", "VISITANTE", "—")
        self._row_tipo_forma = TwoColumnRow("🚗", "TIPO DE ACCESO", "—", "🚶", "FORMA", "—")
        self._row_vigencia   = InfoRow("🕐", "VIGENCIA", "—")
        self._row_acceso     = InfoRow("🕐", "ACCESO", "—")

        info_layout.addWidget(self._row_visitante)
        info_layout.addWidget(_separator())
        info_layout.addWidget(self._row_tipo_forma)
        info_layout.addWidget(_separator())
        info_layout.addWidget(self._row_vigencia)
        info_layout.addWidget(_separator())
        info_layout.addWidget(self._row_acceso)

        card_v.addWidget(info_card)
        card_v.addStretch()

        # Botón "Siguiente Escaneo"
        self._btn_next = QPushButton("Siguiente Escaneo  →")
        self._btn_next.setFixedHeight(56)
        self._btn_next.setFont(QFont("Arial", 16, QFont.Bold))
        self._btn_next.setStyleSheet(
            """
            QPushButton {
                background-color: #1565C0;
                color: white;
                border: none;
                border-radius: 28px;
            }
            QPushButton:hover  { background-color: #1976D2; }
            QPushButton:pressed { background-color: #0D47A1; }
            """
        )
        # No hace nada especial — el timer en MainWindow vuelve a idle
        card_v.addWidget(self._btn_next)

        root.addWidget(card_container, 1)

    # ------------------------------------------------------------------
    # Actualizar datos
    # ------------------------------------------------------------------
    def update_data(self, payload):
        autorizado = payload.status.lower() == "autorizado"

        # Colores del header
        bg_color   = COLOR_GRANTED if autorizado else COLOR_DENIED
        badge_txt  = "ACCESO AUTORIZADO" if autorizado else "ACCESO DENEGADO"
        badge_icon = "✓" if autorizado else "✕"
        title_txt  = "Acceso Concedido" if autorizado else "Acceso Denegado"

        self._header.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            f"stop:0 {bg_color}, stop:1 {'#1B5E20' if autorizado else '#B71C1C'});"
            f"border-bottom-left-radius: 32px; border-bottom-right-radius: 32px;"
        )
        self._badge_icon.setText(badge_icon)
        self._badge_text.setText(badge_txt)
        self._title.setText(title_txt)
        self._sub2.setText(payload.residente)

        # Casa
        self._casa_num.setText(f"#{payload.casa}")

        # Filas
        self._row_visitante.set_value(payload.visitante or "—")
        self._row_tipo_forma.set_values(
            payload.tipo_acceso or "—",
            payload.forma or "—",
        )
        self._row_vigencia.set_value(payload.vigencia or "—")
        self._row_acceso.set_value(payload.acceso or "—")
