import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Database import db  # tu módulo con la conexión a la base

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inicio de Sesión")
        self.setGeometry(600, 300, 350, 180)

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

        # Estilo para el fondo de la ventana y bordes redondeados
        self.setStyleSheet("""
            QWidget {
                background-color: #ffeef2;
                border-radius: 20px;
            }
        """)
        self.usuario_logueado = None  # Aquí guardaremos el usuario válido
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

        # Estética pastel personalizada
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #ffeef2;
                border-radius: 15px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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

        cursor = db.conn.execute("SELECT nombre FROM Usuarios WHERE LOWER(nombre) = LOWER(?)", (username,))
        row = cursor.fetchone()

        if row:
            self.mostrar_mensaje("Bienvenido", f"Bienvenido de nuevo, {username}!", tipo="info")
        else:
            try:
                db.conn.execute("INSERT INTO Usuarios (nombre) VALUES (?)", (username,))
                db.conn.commit()
                self.mostrar_mensaje("Usuario creado", f"Usuario '{username}' creado correctamente.", tipo="info")
            except Exception as e:
                self.mostrar_mensaje("Error", f"No se pudo crear usuario: {e}", tipo="error")
                return

        self.usuario_logueado = username
        self.close()

    def get_usuario(self):
        return self.usuario_logueado



