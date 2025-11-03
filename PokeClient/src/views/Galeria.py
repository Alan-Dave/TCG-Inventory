from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QScrollArea, QGridLayout,
    QHBoxLayout, QLineEdit, QComboBox, QPushButton, QGraphicsOpacityEffect
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QUrl
from PyQt6.QtMultimedia import QSoundEffect
import os
from Backend.get_images import get_pixmap_from_zip

from Database import db  # Conexión a tu base de datos


class ClickableLabel(QLabel):
    # usar object para permitir int o str y evitar coerciones que rompen la búsqueda
    clicked = pyqtSignal(object)

    def __init__(self, id_carta, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_carta = id_carta
        self.seleccionada = False

    def mousePressEvent(self, event):
        self.clicked.emit(self.id_carta)


class GaleriaCartas(QWidget):
    CARTAS_POR_PAGINA = 30

    def __init__(self, path_imagenes):
        super().__init__()
        self.path_imagenes = path_imagenes
        self.labels_por_id = {}
        self.cartas_seleccionadas = set()
        self.current_page = 0
        self.total_cartas = 0

        self.main_layout = QVBoxLayout(self)

        # Filtros
        header_layout = QHBoxLayout()
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("🔍 Buscar carta por nombre...")
        self.timer_busqueda = QTimer()
        self.timer_busqueda.setSingleShot(True)
        self.timer_busqueda.timeout.connect(self.reset_page_and_actualizar)
        self.buscador.textChanged.connect(self.on_text_changed)
        header_layout.addWidget(self.buscador)

        self.filtros = {}
        campos = {
            "rareza": "rarity",
            "tipo": "type",
            "edición": "edition",
            "etapa": "stage",
            "entrenador": "trainer",
            "especial": "especial_type"
        }

        for etiqueta, columna in campos.items():
            combo = QComboBox()
            combo.addItem("Todos")
            combo.setFixedWidth(130)
            combo.currentIndexChanged.connect(self.reset_page_and_actualizar)
            self.filtros[columna] = combo
            header_layout.addWidget(combo)

        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)

        # Área de scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(460)

        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)

        # Transición
        self.opacity_effect = QGraphicsOpacityEffect()
        self.container.setGraphicsEffect(self.opacity_effect)
        self.animacion = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animacion.setDuration(250)

        # Paginación
        paginacion_layout = QHBoxLayout()
        self.btn_anterior = QPushButton("⬅ Anterior")
        self.btn_siguiente = QPushButton("Siguiente ➡")
        self.lbl_pagina = QLabel("")
        self.lbl_pagina.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_anterior.clicked.connect(self.pagina_anterior)
        self.btn_siguiente.clicked.connect(self.pagina_siguiente)

        paginacion_layout.addWidget(self.btn_anterior)
        paginacion_layout.addWidget(self.lbl_pagina)
        paginacion_layout.addWidget(self.btn_siguiente)
        self.main_layout.addLayout(paginacion_layout)

        self.setLayout(self.main_layout)

        # Estilo pastel rosado
        estilo_pastel = """
            QLineEdit {
                padding: 6px;
                border: 2px solid #e7a7c7;
                border-radius: 10px;
                background-color: #ffeaf4;
                color: #5a3e47;
                font-size: 14px;
            }
            QComboBox {
                padding: 4px 8px;
                border: 2px solid #e7a7c7;
                border-radius: 10px;
                background-color: #ffeaf4;
                color: #5a3e47;
                font-size: 13px;
            }
            QComboBox QAbstractItemView {
                background-color: #fff0f6;
                selection-background-color: #f6c1d4;
                color: #5a3e47;
                border: 1px solid #e7a7c7;
                border-radius: 5px;
            }
            QPushButton {
                padding: 6px 12px;
                border: 2px solid #e7a7c7;
                border-radius: 8px;
                background-color: #ffd6e8;
                color: #5a3e47;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #fcd0e4;
            }
            QPushButton:pressed {
                background-color: #fbb8d1;
            }
        """
        self.setStyleSheet(estilo_pastel)

        # Cargar sonido para cambio de página
        self.sonido_pagina = QSoundEffect()
        self.sonido_pagina.setSource(QUrl.fromLocalFile("assets/sounds/paginas.wav"))  # Ajusta la ruta si es necesario
        self.sonido_pagina.setVolume(0.5)

        self.cargar_filtros()
        self.actualizar_total_cartas()
        self.actualizar_galeria()

    def cargar_filtros(self):
        cursor = db.conn.cursor()
        for columna, combo in self.filtros.items():
            cursor.execute(f"SELECT DISTINCT {columna} FROM Cartas WHERE {columna} IS NOT NULL")
            valores = sorted([fila[0] for fila in cursor.fetchall() if fila[0]])
            for val in valores:
                combo.addItem(val)

    def on_text_changed(self):
        self.timer_busqueda.start(300)

    def reset_page_and_actualizar(self):
        self.current_page = 0
        self.actualizar_total_cartas()
        self.actualizar_con_transicion()

    def actualizar_total_cartas(self):
        cursor = db.conn.cursor()
        query = "SELECT COUNT(*) FROM Cartas WHERE 1=1"
        params = []

        texto_busqueda = self.buscador.text().strip().lower()
        if texto_busqueda:
            query += " AND LOWER(nombre) LIKE ?"
            params.append(f"%{texto_busqueda}%")

        for columna, combo in self.filtros.items():
            valor = combo.currentText()
            if valor != "Todos":
                query += f" AND {columna} = ?"
                params.append(valor)

        cursor.execute(query, params)
        self.total_cartas = cursor.fetchone()[0]

    def actualizar_con_transicion(self):
        # Animación de salida (fade out)
        self.animacion.setStartValue(1.0)
        self.animacion.setEndValue(0.0)
        self.animacion.finished.connect(self._actualizar_y_fade_in)
        self.animacion.start()

    def _actualizar_y_fade_in(self):
        self.actualizar_galeria()
        # Animación de entrada (fade in)
        self.animacion.finished.disconnect()
        self.animacion.setStartValue(0.0)
        self.animacion.setEndValue(1.0)
        self.animacion.start()

    def actualizar_galeria(self):
        texto_busqueda = self.buscador.text().strip().lower()

        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.labels_por_id.clear()

        cursor = db.conn.cursor()
        query = "SELECT nombre, id_api FROM Cartas WHERE 1=1"
        params = []

        if texto_busqueda:
            query += " AND LOWER(nombre) LIKE ?"
            params.append(f"%{texto_busqueda}%")

        for columna, combo in self.filtros.items():
            valor = combo.currentText()
            if valor != "Todos":
                query += f" AND {columna} = ?"
                params.append(valor)

        query += " LIMIT ? OFFSET ?"
        params.extend([self.CARTAS_POR_PAGINA, self.current_page * self.CARTAS_POR_PAGINA])

        cursor.execute(query, params)
        cartas = cursor.fetchall()

        row, col = 0, 0
        for nombre, id_api in cartas:
            base = nombre.lower().replace(' ', '_')
            posibles_nombres = [
                f"{base}.webp",
                f"{base}.png",
                f"{base}.jpg",
                f"{base}_{id_api}.webp",
                f"{base}_{id_api}.png",
                f"{base}_{id_api}.jpg",
            ]
            imagen_path = None
            pixmap = None
            for archivo in posibles_nombres:
                # First try to load from zip
                pix = get_pixmap_from_zip(archivo, size=(120, 170))
                if pix:
                    pixmap = pix
                    break
                # Fallback to filesystem
                ruta = os.path.join(self.path_imagenes, archivo)
                if os.path.exists(ruta):
                    pixmap = QPixmap(ruta).scaled(120, 170, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    break
            if not pixmap:
                continue
            label = ClickableLabel(id_api)
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            if id_api in self.cartas_seleccionadas:
                label.setStyleSheet("padding: 5px; border: 2px solid #00cccc; background-color: rgba(0, 255, 200, 80);")
            else:
                label.setStyleSheet("padding: 5px; border: 2px solid transparent;")

            label.clicked.connect(self.seleccionar_carta)
            self.labels_por_id[id_api] = label

            self.grid.addWidget(label, row, col)
            col += 1
            if col == 5:
                col = 0
                row += 1

        total_paginas = max(1, (self.total_cartas + self.CARTAS_POR_PAGINA - 1) // self.CARTAS_POR_PAGINA)
        self.lbl_pagina.setText(f"Página {self.current_page + 1} de {total_paginas}")
        self.btn_anterior.setEnabled(self.current_page > 0)
        self.btn_siguiente.setEnabled(self.current_page < total_paginas - 1)

    def pagina_anterior(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.actualizar_con_transicion()
            self.sonido_pagina.play()  # Reproduce sonido al cambiar página

    def pagina_siguiente(self):
        total_paginas = max(1, (self.total_cartas + self.CARTAS_POR_PAGINA - 1) // self.CARTAS_POR_PAGINA)
        if self.current_page < total_paginas - 1:
            self.current_page += 1
            self.actualizar_con_transicion()
            self.sonido_pagina.play()  # Reproduce sonido al cambiar página

    def seleccionar_carta(self, id_carta):
        label = self.labels_por_id.get(id_carta)
        if not label:
            return

        if id_carta in self.cartas_seleccionadas:
            self.cartas_seleccionadas.remove(id_carta)
            label.setStyleSheet("padding: 5px; border: 2px solid transparent; background-color: transparent;")
        else:
            self.cartas_seleccionadas.add(id_carta)
            label.setStyleSheet("padding: 5px; border: 2px solid #00cccc; background-color: rgba(0, 255, 200, 80);")

    def get_cartas_seleccionadas(self):
        """
        Devuelve la lista de cartas seleccionadas en formato de diccionarios:
        [{"id_api": <id_api>, "nombre": <nombre>}, ...]

        Esto facilita que el código que consume esta función (por ejemplo
        `MainWindow.agregar_cartas`) pueda insertar `nombre` junto al id.
        """
        if not self.cartas_seleccionadas:
            return []

        # Obtener los nombres desde la base de datos para cada id_api seleccionado
        cursor = db.conn.cursor()
        placeholders = ",".join(["?" for _ in self.cartas_seleccionadas])
        query = f"SELECT id_api, nombre FROM Cartas WHERE id_api IN ({placeholders})"
        cursor.execute(query, tuple(self.cartas_seleccionadas))
        rows = cursor.fetchall()

        id_to_nombre = {row[0]: row[1] for row in rows}

        result = []
        for id_api in self.cartas_seleccionadas:
            nombre = id_to_nombre.get(id_api, "")
            result.append({"id_api": id_api, "nombre": nombre})

        return result
