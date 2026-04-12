"""
Pantalla de espera — se muestra cuando no hay escaneo activo.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QFont, QPixmap
import os


class IdleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1A237E;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(24)

        icon = QLabel("🔐")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFont(QFont("Arial", 72))
        icon.setStyleSheet("background: transparent;")
        layout.addWidget(icon)

        title = QLabel("Sistema de Acceso")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(title)

        subtitle = QLabel("Escanea un código QR\npara autorizar el acceso")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Arial", 16))
        subtitle.setStyleSheet("color: rgba(255,255,255,0.7); background: transparent;")
        layout.addWidget(subtitle)

        version = QLabel("Portón BTF · DSD TECH SH-UR01A")
        version.setAlignment(Qt.AlignCenter)
        version.setFont(QFont("Arial", 11))
        version.setStyleSheet("color: rgba(255,255,255,0.35); background: transparent;")
        layout.addWidget(version)
