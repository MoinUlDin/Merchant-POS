# app/windows/screens/pos_screen.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout
from PyQt6.QtCore import Qt
from app.utils.i18n import t

class POSScreen(QWidget):
    def __init__(self, get_lang=lambda: "ur", parent=None):
        super().__init__(parent)
        self.get_lang = get_lang
        self.cart = []
        self._build_ui()
        self.update_texts()

    def _build_ui(self):
        layout = QVBoxLayout()
        self.title = QLabel()
        self.title.setStyleSheet("font-size:18px; font-weight:600;")
        layout.addWidget(self.title)

        scan_row = QHBoxLayout()
        self.scan_input = QLineEdit()
        self.scan_input.setPlaceholderText("")
        self.scan_input.returnPressed.connect(self.fake_scan)
        scan_row.addWidget(self.scan_input)
        self.add_btn = QPushButton()
        self.add_btn.clicked.connect(self.fake_scan)
        scan_row.addWidget(self.add_btn)
        layout.addLayout(scan_row)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Item", "Qty", "Price"])
        layout.addWidget(self.table)

        bottom = QLabel("Checkout controls and totals will be implemented later.")
        layout.addWidget(bottom)
        self.setLayout(layout)

    def update_texts(self):
        lang = self.get_lang()
        self.title.setText(t(lang, "pos_title"))
        self.scan_input.setPlaceholderText(t(lang, "password_placeholder"))  # reuse placeholder key for scan text
        self.add_btn.setText(t(lang, "add_product"))

    def fake_scan(self):
        # very small stub: add a placeholder row to cart (for UI testing)
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem("مثال آئٹم" if self.get_lang()=="ur" else "Sample Item"))
        self.table.setItem(row, 1, QTableWidgetItem("1"))
        self.table.setItem(row, 2, QTableWidgetItem("200.00"))
        self.scan_input.clear()
