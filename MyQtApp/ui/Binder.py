import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
    QGridLayout, QFrame, QPushButton, QApplication, QSizePolicy
)
from PyQt6.QtCore import Qt, QMimeData, QPoint, QSize
from PyQt6.QtGui import QDrag, QPixmap, QCursor, QAction

from ..session import SessionLocal
from ..models import Cartas, UsuarioCarta
from ..app.getImgs import get_pixmap_from_zip

# --- CONSTANTS ---
BINDER_ROWS = 3
BINDER_COLS = 3
SLOTS_PER_PAGE = BINDER_ROWS * BINDER_COLS
# JSON file path: inside assets folder
ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
BINDER_DATA_FILE = os.path.join(ASSETS_DIR, "binder_data.json")

class DraggableCardLabel(QLabel):
    def __init__(self, id_api, pixmap, parent=None):
        super().__init__(parent)
        self.id_api = id_api
        self.setPixmap(pixmap)
        self.setScaledContents(True)
        self.setFixedSize(100, 140)  # Adjust size as needed
        self.setStyleSheet("border: 1px solid #ddd; border-radius: 5px;")
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        
        # Pass card ID and maybe a hint that it comes from inventory
        mime_data.setText(self.id_api)
        drag.setMimeData(mime_data)

        # Set drag pixmap
        drag.setPixmap(self.pixmap().scaled(80, 112, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        drag.setHotSpot(event.pos())

        drag.exec(Qt.DropAction.CopyAction | Qt.DropAction.MoveAction)

class BinderSlot(QLabel):
    def __init__(self, page_index, slot_index, parent=None, binder_view=None):
        super().__init__(parent)
        self.page_index = page_index
        self.slot_index = slot_index
        self.binder_view = binder_view
        self.id_api = None
        
        self.setFixedSize(120, 170)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)
        self.update_style()

    def update_style(self):
        if self.id_api:
            self.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    border: 2px solid #f29ca4;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    background-color: white;
                    border: 2px dashed #f29ca4;
                    border-radius: 8px;
                }
            """)
            self.clear()

    def set_card(self, id_api, pixmap):
        self.id_api = id_api
        if pixmap:
            self.setPixmap(pixmap.scaled(110, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.update_style()
        
    def clear_card(self):
        self.id_api = None
        self.clear()
        self.update_style()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        card_id = event.mimeData().text()
        if card_id:
            # Tell the main view to handle the drop (update logic and UI)
            if self.binder_view:
                self.binder_view.handle_drop(self.page_index, self.slot_index, card_id)
            event.accept()
     
    # Allow dragging FROM the slot too
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.id_api:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not self.id_api:
            return
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.id_api)
        drag.setMimeData(mime_data)
        
        if self.pixmap():
            drag.setPixmap(self.pixmap().scaled(80, 112, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            drag.setHotSpot(event.pos()) # Roughly center?

        # If move action is completed, clear this slot? 
        # For now, let's treat it as a Copy if from inventory, Move if from slot. 
        # But complex to distinguish source. Assume "Move" logic in handle_drop implies clearing previous if unique.
        # For simplicity, we just allow putting copies or moving.
        # To support "Move", we need to know source. 
        # Let's simple Copy for now.
        
        drag.exec(Qt.DropAction.CopyAction)


class InventorySidebar(QWidget):
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.session = SessionLocal()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Search/Header
        self.header = QLabel("Mi Colección")
        self.header.setStyleSheet("font-weight: bold; color: #5a2a3a; font-size: 14px; margin-bottom: 5px;")
        layout.addWidget(self.header)
        
        # Scroll Area for cards
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background-color: #fff7f8; border: none;")
        
        self.container = QWidget()
        self.cards_layout = QVBoxLayout(self.container)
        self.cards_layout.setSpacing(15)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)
        
        self.load_cards()
        
    def load_cards(self):
        # Query distinct cards owned by user
        cartas = (
            self.session.query(Cartas.nombre, Cartas.id_api)
            .join(UsuarioCarta)
            .filter(UsuarioCarta.usuario_nombre == self.usuario)
            .group_by(Cartas.id_api) # distinct items
            .all()
        )
        
        # Clear existing
        for i in reversed(range(self.cards_layout.count())):
            self.cards_layout.itemAt(i).widget().deleteLater()
            
        for nombre, id_api in cartas:
            nombre_archivo = nombre.lower().replace(" ", "_")
            pixmap = get_pixmap_from_zip(nombre_archivo, size=(100, 140), id_api=id_api)
            
            if not pixmap:
                 # Fallback if needed, logic from Inventario.py
                 base_assets = os.path.join(os.path.dirname(__file__), "..", "assets", "images")
                 ruta_alt = os.path.join(base_assets, f"{nombre_archivo}_{id_api}.webp")
                 if os.path.exists(ruta_alt):
                     pixmap = QPixmap(ruta_alt)

            if pixmap:
                card_lbl = DraggableCardLabel(id_api, pixmap)
                self.cards_layout.addWidget(card_lbl)

    def refresh(self):
        self.load_cards()


class BinderPage(QWidget):
    def __init__(self, page_index, binder_view, parent=None):
        super().__init__(parent)
        self.page_index = page_index
        self.binder_view = binder_view
        
        layout = QGridLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.slots = []
        for r in range(BINDER_ROWS):
            for c in range(BINDER_COLS):
                slot_idx = r * BINDER_COLS + c
                slot = BinderSlot(page_index, slot_idx, binder_view=binder_view)
                layout.addWidget(slot, r, c)
                self.slots.append(slot)
                
    def get_slot(self, slot_index):
        if 0 <= slot_index < len(self.slots):
            return self.slots[slot_index]
        return None


class BinderView(QWidget):
    def __init__(self, usuario, parent=None):
        super().__init__(parent)
        self.usuario = usuario
        self.binder_data = {}
        self.current_spread_index = 0 # 0 means pages 0 and 1
        
        self.load_binder_data()
        
        # Main Layout: Splitter logic or simple HBox
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Left Panel: Inventory ---
        left_container = QWidget()
        left_container.setFixedWidth(240) # Sidebar width
        left_container.setStyleSheet("""
            background-color: #ffeef2; 
            border-right: 2px solid #f3c8d1;
        """)
        left_layout = QVBoxLayout(left_container)
        
        self.inventory = InventorySidebar(usuario)
        left_layout.addWidget(self.inventory)
        
        main_layout.addWidget(left_container)
        
        # --- Right Panel: Binder Pages ---
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(20, 20, 20, 10)
        
        # Header / Title
        title = QLabel("Mi Carpeta Física")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #5a2a3a;")
        right_layout.addWidget(title)
        
        # Spread Container (Two pages side by side)
        self.spread_widget = QWidget()
        self.spread_layout = QHBoxLayout(self.spread_widget)
        self.spread_layout.setSpacing(40) # Gap between pages (binder spine)
        self.spread_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # We will dynamically create/update pages
        self.page_left = None
        self.page_right = None
        
        right_layout.addWidget(self.spread_widget, 1) # Expand
        
        # Pagination Controls
        controls_layout = QHBoxLayout()
        self.btn_prev = QPushButton("◀ Anterior")
        self.btn_next = QPushButton("Siguiente ▶")
        self.lbl_pages = QLabel("Páginas 1 - 2")
        
        for btn in [self.btn_prev, self.btn_next]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f7a8b8; color: white; border-radius: 8px; padding: 5px 15px; font-weight: bold; border: 1px solid #e08fa0;
                }
                QPushButton:hover { background-color: #f56b7b; }
            """)
            
        self.btn_prev.clicked.connect(self.prev_spread)
        self.btn_next.clicked.connect(self.next_spread)
        
        controls_layout.addStretch()
        controls_layout.addWidget(self.btn_prev)
        controls_layout.addWidget(self.lbl_pages)
        controls_layout.addWidget(self.btn_next)
        controls_layout.addStretch()
        
        right_layout.addLayout(controls_layout)
        
        main_layout.addWidget(right_container)
        
        # Initialize pages
        self.update_spread()
        
    def load_binder_data(self):
        if os.path.exists(BINDER_DATA_FILE):
            try:
                with open(BINDER_DATA_FILE, 'r') as f:
                    self.binder_data = json.load(f)
            except:
                self.binder_data = {}
        # Ensure user section exists
        if self.usuario not in self.binder_data:
            self.binder_data[self.usuario] = {}
            
    def save_binder_data(self):
        with open(BINDER_DATA_FILE, 'w') as f:
            json.dump(self.binder_data, f, indent=4)
            
    def get_card_at(self, page, slot):
        key = f"{page}_{slot}"
        return self.binder_data[self.usuario].get(key)
        
    def set_card_at(self, page, slot, card_id):
        key = f"{page}_{slot}"
        self.binder_data[self.usuario][key] = card_id
        self.save_binder_data()
        
    def update_spread(self):
        # Clear existing pages from layout
        if self.page_left:
            self.spread_layout.removeWidget(self.page_left)
            self.page_left.deleteLater()
        if self.page_right:
            self.spread_layout.removeWidget(self.page_right)
            self.page_right.deleteLater()
            
        p_idx_1 = self.current_spread_index * 2
        p_idx_2 = p_idx_1 + 1
        
        self.page_left = BinderPage(p_idx_1, self)
        self.page_right = BinderPage(p_idx_2, self)
        
        # Populate slots
        self.populate_page(self.page_left, p_idx_1)
        self.populate_page(self.page_right, p_idx_2)
        
        self.spread_layout.addWidget(self.page_left)
        # Visual spine separator could go here
        self.spread_layout.addWidget(self.page_right)
        
        self.lbl_pages.setText(f"Páginas {p_idx_1 + 1} - {p_idx_2 + 1}")
        self.btn_prev.setEnabled(self.current_spread_index > 0)
        # Allow infinite pages or limit? Let's limit reasonably or just allow infinite
        self.btn_next.setEnabled(True) 

    def populate_page(self, page_widget, page_idx):
        session = SessionLocal()
        for i in range(SLOTS_PER_PAGE):
            card_id = self.get_card_at(page_idx, i)
            slot = page_widget.get_slot(i)
            if card_id and slot:
                 # Fetch card name to get image
                 carta = session.query(Cartas).filter(Cartas.id_api == card_id).first()
                 if carta:
                     nombre_archivo = carta.nombre.lower().replace(" ", "_")
                     pixmap = get_pixmap_from_zip(nombre_archivo, size=(110, 160), id_api=card_id)
                     if not pixmap:
                         # fallback
                         base_assets = os.path.join(os.path.dirname(__file__), "..", "assets", "images")
                         ruta_alt = os.path.join(base_assets, f"{nombre_archivo}_{card_id}.webp")
                         if os.path.exists(ruta_alt):
                             pixmap = QPixmap(ruta_alt)
                     
                     if pixmap:
                         slot.set_card(card_id, pixmap)

    def handle_drop(self, page_idx, slot_idx, card_id):
        # Update data
        self.set_card_at(page_idx, slot_idx, card_id)
        
        # Update UI visually immediately (fetch image again)
        # Or optimization: pass pixmap in mime data? 
        # For now, fetching is safer to ensure consistency
        
        # Find the specific slot widget
        target_page_widget = None
        if page_idx == self.current_spread_index * 2:
            target_page_widget = self.page_left
        elif page_idx == self.current_spread_index * 2 + 1:
            target_page_widget = self.page_right
            
        if target_page_widget:
            slot = target_page_widget.get_slot(slot_idx)
            if slot:
                 session = SessionLocal()
                 carta = session.query(Cartas).filter(Cartas.id_api == card_id).first()
                 if carta:
                     nombre_archivo = carta.nombre.lower().replace(" ", "_")
                     pixmap = get_pixmap_from_zip(nombre_archivo, size=(110, 160), id_api=card_id)
                     if not pixmap:
                         base_assets = os.path.join(os.path.dirname(__file__), "..", "assets", "images")
                         ruta_alt = os.path.join(base_assets, f"{nombre_archivo}_{card_id}.webp")
                         if os.path.exists(ruta_alt):
                             pixmap = QPixmap(ruta_alt)
                     slot.set_card(card_id, pixmap)

    def prev_spread(self):
        if self.current_spread_index > 0:
            self.current_spread_index -= 1
            self.update_spread()
            
    def clear_binder(self):
        # Clear data for this user
        self.binder_data[self.usuario] = {}
        self.save_binder_data()
        self.update_spread()
        
    def next_spread(self):
        self.current_spread_index += 1
        self.update_spread()

    # Should be called if Inventory changes (e.g. from Index)
    def refresh_inventory(self):
        self.inventory.refresh()
