from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QAbstractItemView,
    QHeaderView
)
from PyQt6.QtCore import Qt, QTimer
from app.utils.i18n import t
from ..services.product_service import ProductService


class ProductsListScreen(QWidget):
    def __init__(self, on_add, on_edit, on_stock_reorder, get_lang=lambda: "ur"):
        super().__init__()
        self.on_add = on_add
        self.on_edit = on_edit
        self.get_lang = get_lang
        self.on_stock_reorder = on_stock_reorder
        self.product_service = ProductService()

        # column width ratios (modern, readable)
        self._column_ratios = [3, 2, 2, 2, 2, 2, 1, 2, 2, 2]

        self.init_ui()
        self.apply_styles()
        self.connect_actions()

    def connect_actions(self):
        self.btn_add.clicked.connect(self.on_add)
        self.table.cellDoubleClicked.connect(self.handle_edit)
        self.btn_stock_reorder.clicked.connect(self.on_stock_reorder)
           
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)

        # ---------- Header ----------
        header = QHBoxLayout()
        self.title = QLabel()
        self.title.setStyleSheet("font-size: 20px; font-weight: 600;")
        header.addWidget(self.title)
        header.addStretch()

        self.btn_add = QPushButton()
        self.btn_stock_reorder = QPushButton() 
        header.addWidget(self.btn_add)
        header.addWidget(self.btn_stock_reorder)

        layout.addLayout(header)

        # ---------- Table ----------
        self.table = QTableWidget(0, 0)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

        self.refresh_products()

    # --------------------------------------------------
    # Data
    # --------------------------------------------------
    def refresh_products(self):
        try:
            rows = self.product_service.all_products()
        except Exception as e:
            print("Failed to fetch products:", e)
            rows = []

        lang = self.get_lang() or "ur"

        # ---------- Headers ----------
        if lang == "ur":
            headers = [
                "نام", "شارٹ کوڈ", "کمپنی",
                "قیمت خرید", "قیمت فروخت",
                "اسٹاک", "یونٹ",
                "کھلا وزن", "پیکنگ سائز",
                "کم اسٹاک"
            ]
        else:
            headers = [
                "Name", "Short Code", "Company",
                "Base Price", "Sell Price",
                "Stock", "Unit",
                "Custom Packing", "Packing Size",
                "Reorder Level"
            ]

        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))

        header = self.table.horizontalHeader()
        header.setMinimumSectionSize(80)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # ---------- Helpers ----------
        def price_rs(paisa):
            try:
                return f"{int(paisa) / 100:.2f}"
            except Exception:
                return ""

        def yes_no(v):
            return "✔" if v else "—"

        # ---------- Rows ----------
        for r, row in enumerate(rows):
            (
                prod_id, short_code, ur_name, en_name, company, _barcode,
                base_price, sell_price, stock_qty, reorder_threshold,
                _category_id, unit, custom_packing, packing_size, _supply_pack_qty,
                _created_at, _updated_at
            ) = row

            # name by language
            ur_name = (ur_name or "").strip()
            en_name = (en_name or "").strip()
            name = ur_name if lang == "ur" and ur_name else en_name or ur_name

            items = [
                QTableWidgetItem(name),
                QTableWidgetItem(short_code or ""),
                QTableWidgetItem(company or ""),
                QTableWidgetItem(price_rs(base_price)),
                QTableWidgetItem(price_rs(sell_price)),
                QTableWidgetItem(str(stock_qty)),
                QTableWidgetItem(unit),
                QTableWidgetItem(yes_no(custom_packing)),
                QTableWidgetItem(str(packing_size) if packing_size else "—"),
                QTableWidgetItem(str(reorder_threshold)),
            ]

            # store product id on first column
            items[0].setData(Qt.ItemDataRole.UserRole, prod_id)

            # alignment
            for i, item in enumerate(items):
                if i in (3, 4):  # prices
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                elif i in (5, 6, 7, 8, 9):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

                self.table.setItem(r, i, item)
                
        self._apply_language(lang=lang)

    def _apply_language(self, lang=None):
        # labels
        if lang is None:
            lang = self.get_lang() or 'ur'
            
        self.title.setText("📦 " + t(lang, "products"))
        self.btn_add.setText("＋ " + t(lang, "add_product"))
        self.btn_stock_reorder.setText(t(lang, "stock_reorder"))
        
        QTimer.singleShot(0, self._apply_column_ratios)

    # --------------------------------------------------
    # Interaction
    # --------------------------------------------------
    def handle_edit(self, row, col):
        item = self.table.item(row, 0)
        if not item:
            return
        product_id = item.data(Qt.ItemDataRole.UserRole)
        if product_id:
            self.on_edit(product_id)

    # --------------------------------------------------
    # Styling
    # --------------------------------------------------
    def apply_styles(self):
        self.table.setStyleSheet("""
            QTableView {
                border: 1px solid #dcdcdc;
                border-radius: 6px;
                gridline-color: #eeeeee;
                font-size: 16px;
            }
            QHeaderView::section {
                background: #f5f7fa;
                padding: 6px;
                border: none;
                font-weight: 500;
                font-size: 18px;  
            }
            QTableView::item {
                padding: 4px;
                font-size: 12px;
            }
        """)

    # --------------------------------------------------
    # Column ratios
    # --------------------------------------------------
    def _apply_column_ratios(self):
        if not self._column_ratios:
            return

        cols = self.table.columnCount()
        ratios = self._column_ratios[:cols]
        total = sum(ratios) or cols
        avail = self.table.viewport().width()

        used = 0
        for i in range(cols):
            if i < cols - 1:
                w = int(ratios[i] / total * avail)
            else:
                w = avail - used
            self.table.setColumnWidth(i, max(40, w))
            used += w

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_column_ratios()
