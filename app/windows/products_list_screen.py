from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QAbstractItemView
)
from PyQt6.QtCore import Qt
from app.utils.i18n import t
from ..services.product_service import ProductService


class ProductsListScreen(QWidget):
    def __init__(self, on_add, on_edit, get_lang=lambda: "en"):
        super().__init__()
        self.on_add = on_add
        self.on_edit = on_edit
        self.get_lang = get_lang
        self.product_service = ProductService()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        title = QLabel("📦 " + t(self.get_lang(), "products"))
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()

        btn_add = QPushButton("➕ " + t(self.get_lang(), "add_product"))
        btn_add.clicked.connect(self.on_add)
        header.addWidget(btn_add)

        layout.addLayout(header)

        # initial placeholder, actual header set in refresh_products()
        self.table = QTableWidget(0, 6)
        self.table.cellDoubleClicked.connect(self.handle_edit)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)

        # load data
        self.refresh_products()

    def set_get_lang(self, get_lang):
        """Optional: update the language callable"""
        self.get_lang = get_lang

    def refresh_products(self):
        """
        Fetch data from DB and populate the QTableWidget.
        Shows a single Name column based on language (ur/en) plus other attributes.
        """
        try:
            rows = self.product_service.all_products()
        except Exception as e:
            print("Failed to fetch products:", e)
            rows = []

        lang = self.get_lang() or "en"
        name_label = t(lang, "name") if callable(t) else ("نام" if lang == "ur" else "Name")

        headers = ["ID", name_label, "Company", "Barcode", "Price", "Stock"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            # row mapping per updated all_products:
            # 0=id,1=ur_name,2=en_name,3=company,4=barcode,5=base_price,6=sell_price,7=stock_qty,8=reorder_threshold
            prod_id = row[0]
            ur_name = row[1] or ""
            en_name = row[2] or ""
            company = row[3] or ""
            barcode = row[4] or ""
            # prefer sell_price, fall back to base_price
            sell_price = row[6] if len(row) > 6 and row[6] not in (None, "") else (row[5] if len(row) > 5 else "")
            stock_qty = row[7] if len(row) > 7 else ""

            # choose proper name depending on language
            display_name = ur_name if lang == "ur" else en_name

            # format price
            try:
                price_text = f"{float(sell_price):.2f}"
            except Exception:
                price_text = str(sell_price or "")

            id_item = QTableWidgetItem(str(prod_id))
            name_item = QTableWidgetItem(display_name)
            company_item = QTableWidgetItem(str(company))
            barcode_item = QTableWidgetItem(str(barcode))
            price_item = QTableWidgetItem(price_text)
            stock_item = QTableWidgetItem(str(stock_qty))

            # Alignments: id and price right/center, name right for Urdu
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if lang == "ur":
                name_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            else:
                name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.table.setItem(r, 0, id_item)
            self.table.setItem(r, 1, name_item)
            self.table.setItem(r, 2, company_item)
            self.table.setItem(r, 3, barcode_item)
            self.table.setItem(r, 4, price_item)
            self.table.setItem(r, 5, stock_item)

        self.table.resizeColumnsToContents()

    def handle_edit(self, row, col):
        item = self.table.item(row, 0)
        if not item:
            return
        try:
            product_id = int(item.text())
        except Exception:
            product_id = item.text()
        self.on_edit(product_id)
