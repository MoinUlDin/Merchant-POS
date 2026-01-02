# app/windows/screens/product_form_screen.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton
from app.utils.i18n import t

class ProductFormScreen(QWidget):
    def __init__(self, get_lang=lambda: "ur", navigate=None, parent=None):
        super().__init__(parent)
        self.get_lang = get_lang
        self.navigate = navigate
        self._build_ui()
        self.update_texts()

    def _build_ui(self):
        layout = QVBoxLayout()
        self.title = QLabel()
        self.title.setStyleSheet("font-size:18px; font-weight:600;")
        layout.addWidget(self.title)

        self.ur_lbl = QLabel("اردو نام (لازمی)")
        self.ur_input = QLineEdit()
        layout.addWidget(self.ur_lbl)
        layout.addWidget(self.ur_input)

        self.en_lbl = QLabel("English name (optional)")
        self.en_input = QLineEdit()
        layout.addWidget(self.en_lbl)
        layout.addWidget(self.en_input)

        note = QLabel()
        self.note_lbl = note
        layout.addWidget(note)

        btn_row = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.clicked.connect(lambda: self.navigate("products") if self.navigate else None)
        btn_row.addWidget(self.back_btn)
        self.save_btn = QPushButton()
        # Save intentionally not connected (disabled) per your instruction
        self.save_btn.setEnabled(False)
        btn_row.addWidget(self.save_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)

    def update_texts(self):
        lang = self.get_lang()
        self.title.setText(t(lang, "add_product"))
        self.ur_lbl.setText("اردو نام (لازمی)" if lang=="ur" else "Urdu name (required)")
        self.en_lbl.setText("انگریزی نام (اختیاری)" if lang=="ur" else "English name (optional)")
        self.note_lbl.setText(t(lang, "add_product_note"))
        self.back_btn.setText(t(lang, "back"))
        self.save_btn.setText(t(lang, "save"))
