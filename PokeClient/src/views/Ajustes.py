from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QComboBox, QSpinBox, QSizePolicy, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os


class _CircleIndicator(QLabel):
    def __init__(self, filled=False, size=22, parent=None):
        super().__init__(parent)
        self.filled = filled
        self.size = size
        self.setFixedSize(size, size)
        self.update_style()

    def update_style(self):
        bg = '#f7a8b8' if self.filled else '#ffffff'
        border = '#f29ca4' if self.filled else '#e8c7ce'
        self.setStyleSheet(f"background:{bg}; border:2px solid {border}; border-radius:{self.size//2}px;")


class AjustesWidget(QWidget):
    """Pantalla de ajustes (UI únicamente) reproduciendo el mockup de Canva."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Estilo general de la tarjeta interior
        self.setStyleSheet("""
            QWidget#ajustes_root { background-color: #c87d86; border-radius: 14px; }
            QLabel.header { color: #fff7f8; font-weight: 700; font-size: 18px; }
            QLabel.label_pill { background: #ffffff; color: #d66b78; border-radius: 18px; padding: 8px 16px; }
            QPushButton.pill { background: #fff7f8; color: #d66b78; border: 2px solid #f7a8b8; border-radius: 18px; padding: 6px 14px; }
            QPushButton.pill:pressed { background:#ffdfe6 }
            QPushButton.pill.selected { background: #bff6c7; color: #24603a; border:2px solid #86d99c }
        """)

        self.setObjectName('ajustes_root')

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        # --- Top (no title, only the content as in the mockup) ---
        top_rows = QVBoxLayout()
        top_rows.setSpacing(12)

        # Row helper
        def make_audio_row(text, filled_count=5):
            row = QHBoxLayout()
            # pill label (rounded white)
            lbl = QLabel(text)
            lbl.setProperty('class', 'label_pill')
            lbl.setFont(QFont('Segoe UI', 11))
            lbl.setFixedHeight(36)
            lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            row.addWidget(lbl)

            # speaker icon
            sp = QLabel("🔊")
            sp.setFixedWidth(28)
            sp.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row.addWidget(sp)

            # indicators (10 circles)
            ind_row = QHBoxLayout()
            ind_row.setSpacing(6)
            for i in range(10):
                c = _CircleIndicator(filled=(i < filled_count), size=18)
                ind_row.addWidget(c)
            row.addLayout(ind_row)
            row.addStretch()
            return row

        top_rows.addLayout(make_audio_row('Música', filled_count=6))
        top_rows.addLayout(make_audio_row('Sonido', filled_count=5))

        root.addLayout(top_rows)

        # Divider
        hr = QFrame()
        hr.setFrameShape(QFrame.Shape.HLine)
        hr.setFrameShadow(QFrame.Shadow.Sunken)
        hr.setStyleSheet('color: rgba(0,0,0,0.12);')
        root.addWidget(hr)

        # Font size slider row
        font_row = QHBoxLayout()
        font_pill = QLabel('Tamaño de fuente')
        font_pill.setProperty('class', 'label_pill')
        font_pill.setFixedHeight(36)
        font_row.addWidget(font_pill)

        self.font_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_slider.setRange(8, 30)
        self.font_slider.setValue(14)
        self.font_slider.setFixedHeight(28)
        self.font_slider.setStyleSheet("QSlider::groove:horizontal { height:8px; background:#ffd6dd; border-radius:4px;} QSlider::handle:horizontal{ background:white; border:2px solid #ffc2cc; width:18px; margin:-6px 0; border-radius:9px }")
        font_row.addWidget(self.font_slider)
        root.addLayout(font_row)

        # Small spacer
        root.addSpacing(6)

        # Grid with pill controls (to mimic positions in mockup)
        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(10)

        # Row 0: Tema (Sylveon) | Tamaño Cartas (Normal)
        btn_tema = QPushButton('Sylveon')
        btn_tema.setProperty('class', 'pill')
        btn_tema.setFixedHeight(36)
        lbl_tema = QLabel('Tema')
        lbl_tema.setProperty('class', 'label_pill')
        lbl_tema.setFixedHeight(36)
        grid.addWidget(lbl_tema, 0, 0)
        grid.addWidget(btn_tema, 0, 1)

        lbl_tamcart = QLabel('Tamaño Cartas')
        lbl_tamcart.setProperty('class', 'label_pill')
        lbl_tamcart.setFixedHeight(36)
        btn_tamcart = QPushButton('Normal')
        btn_tamcart.setProperty('class', 'pill')
        btn_tamcart.setFixedHeight(36)
        grid.addWidget(lbl_tamcart, 0, 2)
        grid.addWidget(btn_tamcart, 0, 3)

        # Row 1: Animaciones toggle (SI) | Cambiar Música (1)
        lbl_anim = QLabel('Animaciones')
        lbl_anim.setProperty('class', 'label_pill')
        lbl_anim.setFixedHeight(36)
        grid.addWidget(lbl_anim, 1, 0)

        btn_anim_si = QPushButton('SI')
        btn_anim_si.setProperty('class', 'pill')
        btn_anim_si.setFixedHeight(36)
        # mark selected style via class on the widget
        btn_anim_si.setProperty('class', 'pill selected')
        grid.addWidget(btn_anim_si, 1, 1)

        lbl_cambiar = QLabel('Cambiar Música')
        lbl_cambiar.setProperty('class', 'label_pill')
        lbl_cambiar.setFixedHeight(36)
        grid.addWidget(lbl_cambiar, 1, 2)

        spin_change = QSpinBox()
        spin_change.setRange(0, 10)
        spin_change.setValue(1)
        spin_change.setFixedHeight(36)
        grid.addWidget(spin_change, 1, 3)

        # Row 2: Idioma
        lbl_idioma = QLabel('Idioma')
        lbl_idioma.setProperty('class', 'label_pill')
        lbl_idioma.setFixedHeight(36)
        combo_lang = QComboBox()
        combo_lang.addItems(['Español', 'English'])
        combo_lang.setFixedHeight(36)
        grid.addWidget(lbl_idioma, 2, 0)
        grid.addWidget(combo_lang, 2, 1)

        # Fill remaining columns with spacers
        grid.setColumnStretch(4, 1)

        root.addLayout(grid)

        # Footer buttons
        footer = QHBoxLayout()
        footer.addStretch()
        btn_rest = QPushButton('Restaurar valores')
        btn_save = QPushButton('Guardar')
        for b in (btn_rest, btn_save):
            b.setProperty('class', 'pill')
            b.setFixedHeight(36)
        footer.addWidget(btn_rest)
        footer.addWidget(btn_save)

        root.addLayout(footer)

        # Minimum recommended width so it looks like the design
        self.setMinimumWidth(700)


if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    w = AjustesWidget()
    w.show()
    sys.exit(app.exec())
