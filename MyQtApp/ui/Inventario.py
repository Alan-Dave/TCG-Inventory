from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QScrollArea, QGridLayout,
    QHBoxLayout, QLineEdit, QComboBox, QPushButton, QGraphicsOpacityEffect
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QUrl
from PyQt6.QtMultimedia import QSoundEffect
import os

from ..session import SessionLocal
from ..models import Cartas, UsuarioCarta
from ..app.getImgs import get_pixmap_from_zip
from sqlalchemy import func, and_


class ClickableLabel(QLabel):
    clicked = pyqtSignal(object)

    def __init__(self, id_carta, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_carta = id_carta
        self.seleccionada = False

    def mousePressEvent(self, event):
        self.clicked.emit(self.id_carta)


class GaleriaCartasInventario(QWidget):
    CARTAS_POR_PAGINA = 30

    def __init__(self, path_imagenes, nombre_usuario):
        super().__init__()
        self.path_imagenes = path_imagenes
        self.nombre_usuario = nombre_usuario
        self.labels_por_id = {}
        self.cartas_seleccionadas = set()
        self.current_page = 0
        self.total_cartas = 0

        self.session = SessionLocal()

        # UI --- (NO CAMBIÓ)
        self.main_layout = QVBoxLayout(self)
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

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(460)

        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)

        self.opacity_effect = QGraphicsOpacityEffect()
        self.container.setGraphicsEffect(self.opacity_effect)
        self.animacion = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animacion.setDuration(250)

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

        estilo_pastel = """
            QLineEdit { padding: 6px; border: 2px solid #e7a7c7; border-radius: 10px; background-color: #ffeaf4; }
            QComboBox { padding: 4px 8px; border: 2px solid #e7a7c7; border-radius: 10px; background-color: #ffeaf4; }
            QPushButton { padding: 6px 12px; border: 2px solid #e7a7c7; border-radius: 8px; background-color: #ffd6e8; font-weight:bold;}
        """
        self.setStyleSheet(estilo_pastel)

        self.sonido_pagina = QSoundEffect()
        self.sonido_pagina.setSource(QUrl.fromLocalFile("assets/sounds/paginas.wav"))
        self.sonido_pagina.setVolume(0.5)

        self.cargar_filtros()
        self.actualizar_total_cartas()
        self.actualizar_galeria()


    # ✅ SQLAlchemy: cargar combos
    def cargar_filtros(self):
        for columna, combo in self.filtros.items():
            valores = (
                self.session.query(getattr(Cartas, columna))
                .filter(getattr(Cartas, columna).isnot(None))
                .distinct()
                .all()
            )
            valores = sorted(v[0] for v in valores if v[0])
            for val in valores:
                combo.addItem(val)

    def on_text_changed(self):
        self.timer_busqueda.start(300)

    def reset_page_and_actualizar(self):
        self.current_page = 0
        self.actualizar_total_cartas()
        self.actualizar_con_transicion()

    # ✅ SQLAlchemy conteo
    def actualizar_total_cartas(self):
        q = self.session.query(func.count(Cartas.id_api)).join(UsuarioCarta).filter(
            UsuarioCarta.usuario_nombre == self.nombre_usuario
        )

        texto = self.buscador.text().lower().strip()
        if texto:
            q = q.filter(func.lower(Cartas.nombre).like(f"%{texto}%"))

        for columna, combo in self.filtros.items():
            if combo.currentText() != "Todos":
                q = q.filter(getattr(Cartas, columna) == combo.currentText())

        self.total_cartas = q.scalar()

    def actualizar_con_transicion(self):
        self.animacion.setStartValue(1.0)
        self.animacion.setEndValue(0.0)
        self.animacion.finished.connect(self._actualizar_y_fade_in)
        self.animacion.start()

    def _actualizar_y_fade_in(self):
        self.actualizar_galeria()
        self.animacion.finished.disconnect()
        self.animacion.setStartValue(0.0)
        self.animacion.setEndValue(1.0)
        self.animacion.start()

    # ✅ SQLAlchemy mostrar cartas
    def actualizar_galeria(self):
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            widget.deleteLater()

        texto = self.buscador.text().lower().strip()

        q = self.session.query(Cartas.nombre, Cartas.id_api).join(UsuarioCarta).filter(
            UsuarioCarta.usuario_nombre == self.nombre_usuario
        )
        print(f"\nConsulta SQL para {self.nombre_usuario}:")

        if texto:
            q = q.filter(func.lower(Cartas.nombre).like(f"%{texto}%"))

        for columna, combo in self.filtros.items():
            if combo.currentText() != "Todos":
                q = q.filter(getattr(Cartas, columna) == combo.currentText())

        q = q.limit(self.CARTAS_POR_PAGINA).offset(self.current_page * self.CARTAS_POR_PAGINA)
        cartas = q.all()
        print(f"Cartas encontradas: {len(cartas)}")
        print("Primeras 5 cartas:", cartas[:5])

        row, col = 0, 0
        self.labels_por_id.clear()

        for nombre, id_api in cartas:
            nombre_archivo = nombre.lower().replace(" ", "_")
            print(f"\nIntentando cargar imagen para carta: {nombre} (ID: {id_api})")
            
            # Intentar cargar usando el nombre y el ID
            pixmap = get_pixmap_from_zip(nombre_archivo, size=(120, 170), id_api=id_api)
            
            # Si no se encontró con get_pixmap_from_zip, intentar ruta alternativa
            if not pixmap:
                ruta_alt = os.path.join(self.path_imagenes, f"{nombre_archivo}_{id_api}.webp")
                print(f"Intentando ruta alternativa: {ruta_alt}")
                if os.path.exists(ruta_alt):
                    print("✅ Imagen encontrada en ruta alternativa")
                    pixmap = QPixmap(ruta_alt).scaled(120, 170, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            if not pixmap:
                print("❌ No se pudo cargar ninguna imagen")
                continue

            print(f"Dimensiones del pixmap: {pixmap.width()}x{pixmap.height()}")
            
            label = ClickableLabel(id_api)
            label.setPixmap(pixmap)
            label.setMinimumSize(120, 170)  # Asegurar tamaño mínimo
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            if id_api in self.cartas_seleccionadas:
                label.setStyleSheet("padding: 5px; border: 2px solid #00cccc; background-color: rgba(0,255,200,80);")
            else:
                label.setStyleSheet("padding: 5px; border: 2px solid transparent;")

            label.clicked.connect(self.seleccionar_carta)
            self.labels_por_id[id_api] = label
            self.grid.addWidget(label, row, col)

            col += 1
            if col == 5:
                col = 0
                row += 1

        total_pages = max(1, (self.total_cartas + self.CARTAS_POR_PAGINA - 1) // self.CARTAS_POR_PAGINA)
        self.lbl_pagina.setText(f"Página {self.current_page + 1} de {total_pages}")
        self.btn_anterior.setEnabled(self.current_page > 0)
        self.btn_siguiente.setEnabled(self.current_page < total_pages - 1)

    def pagina_anterior(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.actualizar_con_transicion()
            self.sonido_pagina.play()

    def pagina_siguiente(self):
        total = max(1, (self.total_cartas + self.CARTAS_POR_PAGINA - 1) // self.CARTAS_POR_PAGINA)
        if self.current_page < total - 1:
            self.current_page += 1
            self.actualizar_con_transicion()
            self.sonido_pagina.play()

    def seleccionar_carta(self, id_carta):
        label = self.labels_por_id.get(id_carta)
        if not label:
            return

        if id_carta in self.cartas_seleccionadas:
            self.cartas_seleccionadas.remove(id_carta)
            label.setStyleSheet("padding: 5px; border: 2px solid transparent; background-color: transparent;")
        else:
            self.cartas_seleccionadas.add(id_carta)
            label.setStyleSheet("padding: 5px; border: 2px solid #00cccc; background-color: rgba(0,255,200,80);")

    def get_cartas_seleccionadas(self):
        if not self.cartas_seleccionadas:
            return []

        filas = (
            self.session.query(Cartas.id_api, Cartas.nombre)
            .filter(Cartas.id_api.in_(self.cartas_seleccionadas))
            .all()
        )

        return [{"id_api": f[0], "nombre": f[1]} for f in filas]
