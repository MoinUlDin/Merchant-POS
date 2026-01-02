# app/windows/screens/products_screen.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout
from app.utils.i18n import t
from app.services.db_sqlite3 import get_connection

class ProductsScreen(QWidget):
    def __init__(self, get_lang=lambda: "ur", navigate=None, parent=None):
        super().__init__(parent)
        self.get_lang = get_lang
        self.navigate = navigate  # function to navigate between screens
        self._build_ui()
        self.refresh_table()
        self.update_texts()

    def _build_ui(self):
        layout = QVBoxLayout()
        self.title = QLabel()
        self.title.setStyleSheet("font-size:18px; font-weight:600;")
        layout.addWidget(self.title)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton()
        self.add_btn.clicked.connect(lambda: self.navigate("product_form") if self.navigate else None)
        btn_row.addWidget(self.add_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Urdu Name", "English Name", "Stock", "Sell Price"])
        layout.addWidget(self.table)
        self.setLayout(layout)

    def update_texts(self):
        lang = self.get_lang()
        self.title.setText(t(lang, "products_title"))
        self.add_btn.setText(t(lang, "add_product"))

    def refresh_table(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT ur_name, en_name, stock_qty, sell_price FROM products ORDER BY id;")
        rows = cur.fetchall()
        self.table.setRowCount(0)
        for r in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(r["ur_name"])))
            self.table.setItem(row, 1, QTableWidgetItem(str(r["en_name"] or "")))
            self.table.setItem(row, 2, QTableWidgetItem(str(r["stock_qty"])))
            self.table.setItem(row, 3, QTableWidgetItem(f"{r['sell_price']:.2f}"))
