
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

from ..session import SessionLocal
from ..models import Usuarios


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inicio de Sesión")
        self.setGeometry(600, 300, 350, 180)

        self.session = SessionLocal()

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.label = QLabel("Ingresa tu nombre de usuario:")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 16px; font-weight: 600; color: #a85a7c;")

        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Nombre de usuario")
        self.input_username.setFixedHeight(35)
        self.input_username.setStyleSheet("""
            QLineEdit {
                border: 2px solid #f3c6d3;
                border-radius: 12px;
                padding-left: 10px;
                background-color: #fff0f6;
                font-size: 14px;
                color: #5a3e4a;
            }
            QLineEdit:focus {
                border-color: #d46a6a;
                background-color: #ffe3e3;
            }
        """)

        self.btn_login = QPushButton("Entrar / Crear usuario")
        self.btn_login.setFixedHeight(40)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #f7a8b8;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 15px;
                border: 2px solid #f29ca4;
            }
            QPushButton:hover {
                background-color: #f56b7b;
                border-color: #f5475c;
            }
            QPushButton:pressed {
                background-color: #d44854;
                border-color: #b33a46;
            }
        """)
        self.btn_login.clicked.connect(self.handle_login)

        layout.addWidget(self.label)
        layout.addWidget(self.input_username)
        layout.addWidget(self.btn_login)

        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #ffeef2;
                border-radius: 20px;
            }
        """)

        self.usuario_logueado = None


    def mostrar_mensaje(self, titulo, mensaje, tipo="info"):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)

        if tipo == "info":
            msg_box.setIcon(QMessageBox.Icon.Information)
        elif tipo == "warning":
            msg_box.setIcon(QMessageBox.Icon.Warning)
        elif tipo == "error":
            msg_box.setIcon(QMessageBox.Icon.Critical)

        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #ffeef2;
                border-radius: 15px;
                font-size: 14px;
                color: #5a2a3a;
            }
            QPushButton {
                background-color: #f7a8b8;
                color: white;
                border-radius: 10px;
                padding: 8px 15px;
                font-weight: 600;
                min-width: 80px;
                margin: 5px;
                border: 2px solid #f29ca4;
            }
            QPushButton:hover {
                background-color: #f56b7b;
                border-color: #f5475c;
            }
            QPushButton:pressed {
                background-color: #d44854;
                border-color: #b33a46;
            }
        """)

        msg_box.exec()


    def handle_login(self):
        username = self.input_username.text().strip()

        if not username:
            self.mostrar_mensaje("Error", "Debes ingresar un nombre de usuario.", tipo="warning")
            return

        user = self.session.query(Usuarios).filter(Usuarios.nombre.ilike(username)).first()

        if user:
            self.mostrar_mensaje("Bienvenido", f"Bienvenido de nuevo, {username}!", tipo="info")
        else:
            try:
                nuevo = Usuarios(nombre=username)
                self.session.add(nuevo)
                self.session.commit()
                self.mostrar_mensaje("Usuario creado", f"Usuario '{username}' creado correctamente.", tipo="info")
            except Exception as e:
                self.session.rollback()
                self.mostrar_mensaje("Error", f"No se pudo crear usuario: {e}", tipo="error")
                return

        self.usuario_logueado = username
        self.close()


    def get_usuario(self):
        return self.usuario_logueado
