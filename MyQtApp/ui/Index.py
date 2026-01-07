import random
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QMessageBox, QStackedWidget
)
from PyQt6.QtCore import Qt, QUrl, QPropertyAnimation, QEasingCurve, QPoint, QByteArray
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput
import os
import sqlite3 as sql

from .Galeria import GaleriaCartas
from .Inventario import GaleriaCartasInventario
from .Ajustes import AjustesWidget
from .Binder import BinderView


class BotonConSonido(QPushButton):
    def __init__(self, texto, parent=None):
        super().__init__(texto, parent)

        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "sounds"))

        self.hover_sound = QSoundEffect()
        self.hover_sound.setSource(QUrl.fromLocalFile(os.path.join(base_path, "hover.wav")))
        self.hover_sound.setVolume(0.3)

        self.click_sound = QSoundEffect()
        self.click_sound.setSource(QUrl.fromLocalFile(os.path.join(base_path, "click.wav")))
        self.click_sound.setVolume(0.8)

        self.setMouseTracking(True)

    def enterEvent(self, event):
        self.hover_sound.play()
        super().enterEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.click_sound.play()
        super().mousePressEvent(event)


class MainWindow(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle(f"Menú Principal - Usuario: {usuario.capitalize()}")
        self.setGeometry(550, 250, 1000, 650)

        main_layout = QHBoxLayout(self)

        # Barra lateral
        nav_layout = QVBoxLayout()


        # Rutas absolutas a assets (asegura que funcionen tras mover archivos)
        base_assets = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
        iconoBuscar = QIcon(os.path.join(base_assets, "icons", "buscar.png"))
        iconoCarpeta = QIcon(os.path.join(base_assets, "icons", "carpeta.png"))
        iconoColeccion = QIcon(os.path.join(base_assets, "icons", "coleccion.png"))
        # Ruta absoluta a la carpeta de imágenes (ahora en assets/images)
        ruta_imagenes = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "images"))

        self.btn_buscar = BotonConSonido(iconoBuscar, "Buscar cartas")
        self.btn_ver_carpeta = BotonConSonido(iconoCarpeta, "Ver carpeta física")
        self.btn_mi_coleccion = BotonConSonido(iconoColeccion, "Mi colección de cartas")

        botones_principales = [
            self.btn_buscar,
            self.btn_ver_carpeta,
            self.btn_mi_coleccion,
            # botón ajustes: añadimos texto simple con icono si existe
            BotonConSonido("⚙️ Ajustes"),
        ]

        for btn in botones_principales:
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

        # guardamos referencia al botón de ajustes (último botón creado)
        self.btn_ajustes = botones_principales[-1]

        nav_layout.addSpacing(30)

        self.btn_agregar = BotonConSonido("➕ Agregar")
        self.btn_eliminar = BotonConSonido("🗑️ Eliminar")
        self.btn_vaciar = BotonConSonido("⚠️ Vaciar")

        botones_secundarios_layout = QVBoxLayout()
        for btn in [self.btn_agregar, self.btn_eliminar, self.btn_vaciar]:
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #c8a2c8;
                    color: white;
                    font-weight: 600;
                    font-size: 13px;
                    border-radius: 12px;
                    border: 2px solid #b484b4;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #bb8fbb;
                    border-color: #a371a3;
                }
                QPushButton:pressed {
                    background-color: #9e6f9e;
                    border-color: #815d81;
                }
            """)
            botones_secundarios_layout.addWidget(btn)
            botones_secundarios_layout.addSpacing(10)

        nav_layout.addLayout(botones_secundarios_layout)
        nav_layout.addStretch()

        self.btn_salir = BotonConSonido("🚪 Salir del programa")
        self.btn_salir.setFixedHeight(50)
        self.btn_salir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_salir.setStyleSheet("""
            QPushButton {
                background-color: #f78fb3;
                color: white;
                font-weight: 700;
                font-size: 16px;
                border-radius: 14px;
                border: 2px solid #b52b2b;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #c9302c;
                border-color: #8b1c1c;
            }
            QPushButton:pressed {
                background-color: #a92727;
                border-color: #6a1818;
            }
        """)
        nav_layout.addWidget(self.btn_salir)
        nav_layout.addSpacing(20)

        # Estilo del panel lateral para parecer un panel rosa lateral
        side_widget = QWidget()
        side_layout_wrapper = QVBoxLayout(side_widget)
        side_layout_wrapper.setContentsMargins(12, 12, 12, 12)
        side_widget.setStyleSheet("""
            QWidget#side {
                background-color: qlineargradient(x1:0 y1:0, x2:0 y2:1, stop:0 #ffe1ea, stop:1 #ffd6e6);
                border-radius: 18px;
                border: 2px solid #f3c8d1;
            }
        """)
        side_widget.setObjectName('side')
        # mover los widgets del nav_layout al envoltorio visual
        side_layout_wrapper.addLayout(nav_layout)
        side_layout_wrapper.addStretch()

        main_layout.addWidget(side_widget, 1)

        # Páginas con transición
        self.paginas = QStackedWidget()
        self.paginas.addWidget(GaleriaCartas(ruta_imagenes))       # índice 0
        self.paginas.addWidget(BinderView(self.usuario))           # índice 1 - Carpeta
        self.paginas.addWidget(GaleriaCartasInventario(ruta_imagenes, self.usuario))  # índice 2
        self.paginas.addWidget(AjustesWidget())  # índice 3 - pantalla de ajustes (frontend)

        # Contenedor para el área principal (permite agregar overlay y pie)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(14, 14, 14, 14)
        content_layout.setSpacing(8)

        # Estilizado del área principal para asemejar el marco central de la imagen
        content_widget.setStyleSheet("""
            QWidget#content {
                background-color: #fff7f8;
                border: 3px solid #f2d8db;
                border-radius: 12px;
            }
        """)
        content_widget.setObjectName('content')

        # Agregar el QStackedWidget dentro del contenedor
        content_layout.addWidget(self.paginas)

        # Pie inferior del contenido: espacio para paginador y botones de vista
        bottom_bar = QWidget()
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(6, 6, 6, 6)
        bottom_layout.setSpacing(8)

        # Spacer izquierdo (permite empujar el paginador y los botones a la derecha)
        from PyQt6.QtWidgets import QSpacerItem, QSizePolicy
        bottom_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # --- Botones de modo de vista (esquina inferior derecha) ---
        view_buttons = QWidget()
        vb_layout = QHBoxLayout(view_buttons)
        vb_layout.setContentsMargins(0, 0, 0, 0)
        vb_layout.setSpacing(8)

        # Botón vista en cuadrícula (seleccionado por defecto)
        self.btn_view_grid = QPushButton("▦")
        self.btn_view_grid.setFixedSize(48, 48)
        self.btn_view_grid.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_view_grid.setToolTip("Vista en imágenes")
        self.btn_view_grid.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0 y1:0, x2:0 y2:1, stop:0 #d7a8e0, stop:1 #c48ad6);
                color: white;
                border-radius: 12px;
                font-size: 20px;
                font-weight: 700;
                border: 2px solid #b07ab9;
                box-shadow: 0px 2px 6px rgba(0,0,0,0.12);
            }
            QPushButton:pressed { transform: translateY(1px); }
        """)

        # Botón vista en lista (no seleccionado)
        self.btn_view_list = QPushButton("≡")
        self.btn_view_list.setFixedSize(48, 48)
        self.btn_view_list.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_view_list.setToolTip("Vista en lista")
        self.btn_view_list.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                color: #5a2a3a;
                border-radius: 12px;
                font-size: 20px;
                font-weight: 700;
                border: 2px solid #e0d3d6;
            }
            QPushButton:pressed { transform: translateY(1px); }
        """)

        vb_layout.addWidget(self.btn_view_grid)
        vb_layout.addWidget(self.btn_view_list)

        bottom_layout.addWidget(view_buttons, 0, Qt.AlignmentFlag.AlignRight)

        content_layout.addWidget(bottom_bar)

        # Añadir el contenedor al layout principal en lugar del widget directo
        main_layout.addWidget(content_widget, 4)

        # Conexiones de navegación con animación
        self.btn_buscar.clicked.connect(lambda: self.animar_transicion(0))
        self.btn_ver_carpeta.clicked.connect(lambda: self.animar_transicion(1))
        self.btn_mi_coleccion.clicked.connect(lambda: self.animar_transicion(2))
        self.btn_ajustes.clicked.connect(lambda: self.animar_transicion(3))
        self.btn_salir.clicked.connect(self.confirmar_salir)
        self.btn_agregar.clicked.connect(self.agregar_cartas)
        # conectar eliminar (solo visible en la página de inventario)
        self.btn_eliminar.clicked.connect(self.eliminar_cartas)
        self.btn_vaciar.clicked.connect(self.vaciar_binder)

        self.actualizar_botones_secundarios(0)

        self.setStyleSheet("""
            QWidget {
                background-color: #ffeef2;
                border-radius: 20px;
            }
        """)

        # Seleccionar música aleatoria
        musica = random.choice(["musica_fondo_1.mp3", "musica_fondo_2.mp3", "musica_fondo_3.mp3"])

        # Ruta absoluta a la carpeta de sonidos
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "sounds"))
        ruta_musica = os.path.join(base_path, musica)

        # Configurar audio
        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(QUrl.fromLocalFile(ruta_musica))

        # 🔁 Bucle infinito (forma correcta en PyQt6)
        self.player.setLoops(QMediaPlayer.Loops.Infinite)  # ✅ si tu versión lo soporta
        # o, si no funciona en tu versión, usa:
        # self.player.setLoops(-1)

        self.audio_output.setVolume(0.2)
        self.player.play()

    def animar_transicion(self, nuevo_indice):
        indice_actual = self.paginas.currentIndex()
        if nuevo_indice == indice_actual:
            return

        direccion = 1 if nuevo_indice > indice_actual else -1

        widget_actual = self.paginas.currentWidget()
        widget_nuevo = self.paginas.widget(nuevo_indice)

        widget_nuevo.move(direccion * self.paginas.width(), 0)
        widget_nuevo.show()

        anim_nuevo = QPropertyAnimation(widget_nuevo, b"pos", self)
        anim_nuevo.setDuration(400)
        anim_nuevo.setStartValue(widget_nuevo.pos())
        anim_nuevo.setEndValue(QPoint(0, 0))
        anim_nuevo.setEasingCurve(QEasingCurve.Type.InOutCubic)

        anim_actual = QPropertyAnimation(widget_actual, b"pos", self)
        anim_actual.setDuration(400)
        anim_actual.setStartValue(widget_actual.pos())
        anim_actual.setEndValue(QPoint(-direccion * self.paginas.width(), 0))
        anim_actual.setEasingCurve(QEasingCurve.Type.InOutCubic)

        anim_nuevo.start()
        anim_actual.start()

        def on_finish():
            self.paginas.setCurrentIndex(nuevo_indice)
            widget_actual.hide()
            self.actualizar_botones_secundarios(nuevo_indice)
        anim_nuevo.finished.connect(on_finish)

    def cambiar_cuenta(self):
        self.close()
        from .Login import LoginWindow
        self.ventana_login = LoginWindow()
        self.ventana_login.show()

    def actualizar_botones_secundarios(self, indice):
        # Mostrar/ocultar botones según la página activa
        try:
            self.btn_agregar.setVisible(indice == 0)
            self.btn_eliminar.setVisible(indice == 2)
            self.btn_vaciar.setVisible(indice == 1)
        except Exception:
            pass

        # Si entramos a Binder (índice 1), refrescar inventario lateral
        if indice == 1:
            try:
                binder = self.paginas.widget(1)
                if hasattr(binder, 'refresh_inventory'):
                    binder.refresh_inventory()
            except Exception:
                pass

        # Si entramos a la vista de inventario, asegurarnos de refrescar su contenido
        if indice == 2:
            try:
                inventario = self.paginas.widget(2)
                if hasattr(inventario, 'reset_page_and_actualizar'):
                    inventario.reset_page_and_actualizar()
                else:
                    if hasattr(inventario, 'actualizar_total_cartas'):
                        inventario.actualizar_total_cartas()
                    if hasattr(inventario, 'actualizar_galeria'):
                        inventario.actualizar_galeria()
            except Exception:
                pass

    def confirmar_salir(self):
        self.mostrar_mensaje("¿Seguro que quieres salir del programa?",
                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                             cerrar=True)

    def agregar_cartas(self):
        galeria_busqueda = self.paginas.widget(0)
        cartas_seleccionadas = galeria_busqueda.get_cartas_seleccionadas()

        if not cartas_seleccionadas:
            self.mostrar_mensaje("Selecciona al menos una carta para agregar.")
            return

        conn = sql.connect("PokeDatabase.db")
        cursor = conn.cursor()

        exitos = 0
        for carta in cartas_seleccionadas:
            try:
                cursor.execute(
                    "INSERT INTO usuario_carta (usuario_nombre, carta_id) VALUES (?, ?)",
                    (self.usuario, carta["id_api"])
                )
                exitos += 1
            except sql.IntegrityError:
                pass

        conn.commit()
        conn.close()

        if exitos:
            self.mostrar_mensaje(f"✔️ Se han agregado {exitos} carta(s) a tu colección.")
            # Refrescar la vista de inventario si existe
            try:
                inventario = self.paginas.widget(2)
                if hasattr(inventario, 'reset_page_and_actualizar'):
                    inventario.reset_page_and_actualizar()
                else:
                    if hasattr(inventario, 'actualizar_total_cartas'):
                        inventario.actualizar_total_cartas()
                    if hasattr(inventario, 'actualizar_galeria'):
                        inventario.actualizar_galeria()
            except Exception:
                pass
        else:
            self.mostrar_mensaje("❗Las cartas seleccionadas ya están en tu colección.")

    def mostrar_mensaje(self, texto, botones=QMessageBox.StandardButton.Ok, cerrar=False):
        mensaje = QMessageBox(self)
        mensaje.setWindowTitle("Confirmación" if cerrar else "Información")
        mensaje.setText(texto)
        mensaje.setStandardButtons(botones)
        mensaje.setDefaultButton(QMessageBox.StandardButton.Ok)
        mensaje.setStyleSheet("""
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

        resultado = mensaje.exec()
        if cerrar and resultado == QMessageBox.StandardButton.Yes:
            self.close()

    def eliminar_cartas(self):
        """
        Elimina las cartas seleccionadas de la tabla usuario_carta para el usuario actual.
        Muestra confirmación antes de borrar y refresca la vista de inventario.
        """
        # Obtener el widget de inventario
        try:
            inventario = self.paginas.widget(2)
        except Exception:
            inventario = None

        if inventario is None:
            self.mostrar_mensaje("No se pudo acceder al inventario.")
            return

        # Pedir las cartas seleccionadas
        try:
            cartas = inventario.get_cartas_seleccionadas()
        except Exception:
            cartas = []

        if not cartas:
            self.mostrar_mensaje("Selecciona al menos una carta de tu inventario para eliminar.")
            return

        # Preparar texto de confirmación
        nombres = [c.get('nombre', c.get('id_api')) if isinstance(c, dict) else str(c) for c in cartas]
        texto = f"¿Seguro que quieres eliminar {len(nombres)} carta(s) de tu inventario?\n\n"
        texto += ", ".join(nombres[:6])
        if len(nombres) > 6:
            texto += ", ..."

        resp = QMessageBox.question(self, "Confirmar eliminación", texto,
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resp != QMessageBox.StandardButton.Yes:
            return

        # Ejecutar eliminación en la base de datos (solo para este usuario)
        conn = sql.connect("PokeDatabase.db")
        cursor = conn.cursor()
        eliminados = 0
        for c in cartas:
            id_api = c.get('id_api') if isinstance(c, dict) else c
            if not id_api:
                continue
            cursor.execute("DELETE FROM usuario_carta WHERE usuario_nombre = ? AND carta_id = ?", (self.usuario, id_api))
            eliminados += cursor.rowcount if cursor.rowcount else 0

        conn.commit()
        conn.close()

        if eliminados:
            self.mostrar_mensaje(f"✔️ Se han eliminado {eliminados} carta(s) de tu inventario.")
        else:
            self.mostrar_mensaje("❗No se eliminaron cartas (posiblemente ya no existían en la tabla).")

        # Refrescar inventario
        try:
            if hasattr(inventario, 'reset_page_and_actualizar'):
                inventario.reset_page_and_actualizar()
            else:
                if hasattr(inventario, 'actualizar_total_cartas'):
                    inventario.actualizar_total_cartas()
                if hasattr(inventario, 'actualizar_galeria'):
                    inventario.actualizar_galeria()
        except Exception:
            pass

    def vaciar_binder(self):
        resp = QMessageBox.question(self, "Vaciar Carpeta", "¿Estás seguro de que quieres quitar todas las cartas de la carpeta?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resp == QMessageBox.StandardButton.Yes:
            try:
                binder = self.paginas.widget(1)
                binder.clear_binder()
                self.mostrar_mensaje("✔️ Carpeta vaciada correctamente.")
            except Exception:
                self.mostrar_mensaje("Error al vaciar la carpeta.")
