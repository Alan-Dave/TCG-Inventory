from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QScrollArea, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont



class MainWindow(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle(f"Menú Principal - Usuario: {usuario.capitalize()}")
        self.setGeometry(550, 250, 900, 600)

        # Layout principal horizontal
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Barra de navegación vertical (izquierda)
        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(12)

        self.btn_ver_cartas = QPushButton("📚 Ver como carpeta física")
        self.btn_buscar = QPushButton("🔍 Buscar cartas por nombre")
        self.btn_mi_coleccion = QPushButton("🎴 Mi colección de cartas")
        self.btn_cambiar_cuenta = QPushButton("🔄 Cambiar de cuenta")
        self.btn_salir = QPushButton("🚪 Salir del programa")

        for btn in (self.btn_ver_cartas, self.btn_buscar, self.btn_mi_coleccion,
                    self.btn_cambiar_cuenta, self.btn_salir):
            btn.setFixedHeight(45)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f7a8b8;
                    color: white;
                    font-weight: 600;
                    font-size: 14px;
                    border-radius: 12px;
                    border: 2px solid #f29ca4;
                    text-align: left;
                    padding-left: 15px;
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
            nav_layout.addWidget(btn)

        # Añadir espacio para que botones queden arriba
        nav_layout.addStretch()

        # Panel derecho para "cartas"
        self.cartas_widget = QWidget()
        self.cartas_layout = QVBoxLayout()
        self.cartas_layout.setContentsMargins(10, 10, 10, 10)
        self.cartas_layout.setSpacing(10)

        # Título sección cartas
        titulo_cartas = QLabel("Cartas descubiertas")
        titulo_cartas.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        titulo_cartas.setStyleSheet("color: #a85a7c; margin-bottom: 10px;")
        self.cartas_layout.addWidget(titulo_cartas)

        # Lista scrollable de cartas
        self.lista_cartas = QListWidget()
        self.lista_cartas.setStyleSheet("""
            QListWidget {
                background-color: #fff0f6;
                border: 2px solid #f3c6d3;
                border-radius: 15px;
                padding: 8px;
                font-size: 14px;
                color: #5a3e4a;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f7d4db;
            }
            QListWidget::item:selected {
                background-color: #f29ca4;
                color: white;
                border-radius: 12px;
            }
        """)

        # Ejemplo: agregar cartas (puedes reemplazarlo por tus datos reales)
        for i in range(1, 31):
            item = QListWidgetItem(f"Carta {i}: Nombre de la carta {i}")
            self.lista_cartas.addItem(item)

        self.cartas_layout.addWidget(self.lista_cartas)
        self.cartas_widget.setLayout(self.cartas_layout)

        # Agregar barra navegación y sección cartas al layout principal
        main_layout.addLayout(nav_layout, 1)  # 1 parte del ancho para nav
        main_layout.addWidget(self.cartas_widget, 4)  # 4 partes para cartas

        # Fondo y bordes redondeados de la ventana principal
        self.setStyleSheet("""
            QWidget {
                background-color: #ffeef2;
                border-radius: 20px;
            }
        """)

        self.setLayout(main_layout)



