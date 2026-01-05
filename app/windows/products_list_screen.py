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
    def __init__(self, on_add, on_edit, get_lang=lambda: "ur"):
        super().__init__()
        self.on_add = on_add
        self.on_edit = on_edit
        self.get_lang = get_lang
        self.product_service = ProductService()

        # if None -> equal Stretch mode (default). Otherwise a list of numbers used as ratios.
        self._column_ratios = [4,3,2,2,2,2,2]

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)

        header = QHBoxLayout()
        title = QLabel("📦 " + t(self.get_lang(), "products"))
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()

        self.btn_add = QPushButton("+" + t(self.get_lang(), "add_product"))
        self.btn_add.clicked.connect(self.on_add)
        header.addWidget(self.btn_add)

        layout.addLayout(header)

        # table: columns set dynamically in refresh_products()
        self.table = QTableWidget(0, 0)
        self.table.cellDoubleClicked.connect(self.handle_edit)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        layout.addWidget(self.table)

        # load data
        self.refresh_products()

    def set_get_lang(self, get_lang):
        """Optional: update the language callable"""
        self.get_lang = get_lang

    def showEvent(self, event):
        super().showEvent(event)
        # schedule a column ratio pass after widget is shown and layouted
        if self._column_ratios:
            QTimer.singleShot(0, self._apply_column_ratios)
            
    def refresh_products(self):
        """
        Fetch rows and populate the table.
        Columns shown: Name (one column), Company, Barcode, Base Price, Sell Price, Stock, Reorder Threshold
        Product id is stored on the name_item under Qt.UserRole (no id column displayed).
        """
        print("into Refresh Products")
        try:
            rows = self.product_service.all_products()
        except Exception as e:
            print("Failed to fetch products:", e)
            rows = []

        lang = self.get_lang() or "ur"

        if lang == "ur":
            headers = ['نام', "کمپنی", "بارکوڈ", "قیمت خرید", "قیمت فروخت", "تعداد", "کم تعداد"]
        else:
            headers = ['Name', "Company", "Barcode", "Base Price", "Sell Price", "Stock", "Low Stock"]

        # set up columns and headers
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        # If no custom ratios set, use equal Stretch so columns fill available width.
        header = self.table.horizontalHeader()
        header.setMinimumSectionSize(40)

        if not self._column_ratios:
            for col in range(self.table.columnCount()):
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
        else:
            # ensure header is in Interactive mode for explicit widths
            for col in range(self.table.columnCount()):
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)

            
            
        

        # populate rows
        self.table.setRowCount(len(rows))

        for r, row in enumerate(rows):
            # row mapping:
            # 0=id,1=ur_name,2=en_name,3=company,4=barcode,5=base_price,6=sell_price,7=stock_qty,8=reorder_threshold
            prod_id = row[0]
            ur_name = (row[1] or "").strip()
            en_name = (row[2] or "").strip()
            company = row[3] or ""
            barcode = row[4] or ""
            base_price = row[5] if len(row) > 5 else ""
            sell_price = row[6] if len(row) > 6 else ""
            stock_qty = row[7] if len(row) > 7 else ""
            reorder_threshold = row[8] if len(row) > 8 else ""

            # choose the display name using fallback rules
            if lang == "en":
                display_name = en_name if en_name != "" else ur_name
            else:  # ur
                display_name = ur_name if ur_name != "" else en_name

            # pretty-format prices if possible
            def fmt_price(x):
                try:
                    return f"{float(x):.2f}"
                except Exception:
                    return str(x or "")

            base_price_text = fmt_price(base_price)
            sell_price_text = fmt_price(sell_price)

            # Create items
            name_item = QTableWidgetItem(display_name)
            company_item = QTableWidgetItem(str(company))
            barcode_item = QTableWidgetItem(str(barcode))
            base_price_item = QTableWidgetItem(base_price_text)
            sell_price_item = QTableWidgetItem(sell_price_text)
            stock_item = QTableWidgetItem(str(stock_qty))
            reorder_threshold_item = QTableWidgetItem(str(reorder_threshold))

            # store product id on name_item so we can open editor without showing id
            name_item.setData(Qt.ItemDataRole.UserRole, prod_id)

            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            base_price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            sell_price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            reorder_threshold_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Insert into table (no id column)
            self.table.setItem(r, 0, name_item)
            self.table.setItem(r, 1, company_item)
            self.table.setItem(r, 2, barcode_item)
            self.table.setItem(r, 3, base_price_item)
            self.table.setItem(r, 4, sell_price_item)
            self.table.setItem(r, 5, stock_item)
            self.table.setItem(r, 6, reorder_threshold_item)

        # update add button label (language-sensitive)
        self.btn_add.setText("+" + t(self.get_lang(), "add_product"))

    def handle_edit(self, row, col):
        # get product id from name item UserRole
        name_item = self.table.item(row, 0)
        if not name_item:
            return
        product_id = name_item.data(Qt.ItemDataRole.UserRole)
        if product_id is None:
            print("Could not determine product id for row", row)
            return
        self.on_edit(product_id)

    def apply_styles(self):
        # add padding inside cells (visual only)
        self.table.setStyleSheet("QTableView::item { padding: 6px 6px; }")

    # -----------------------
    # Column ratio helpers
    # -----------------------
    def set_column_ratios(self, ratios):
        """
        Set column width ratios.
        `ratios` should be an iterable of numbers. Length may be >= columnCount.
        Example: [3,1,1,1,1,1,1] makes first column 3x wider than each other.
        If ratios is None or empty, the table will use equal Stretch mode.
        """
        if not ratios:
            self._column_ratios = None
            # revert to Stretch mode
            header = self.table.horizontalHeader()
            for col in range(self.table.columnCount()):
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
            return

        # store ratios and try to apply immediately (may be applied later on resize)
        self._column_ratios = list(ratios)
        self._apply_column_ratios()

    def _apply_column_ratios(self):
        """Compute widths from ratios and set explicit column widths."""
        if not self._column_ratios:
            return
        cols = self.table.columnCount()
        if cols == 0:
            return  # nothing to do yet

        # use only as many ratios as columns (if shorter, pad with 1s)
        ratios = self._column_ratios[:cols]
        if len(ratios) < cols:
            ratios = ratios + [1] * (cols - len(ratios))

        # normalize (protect against all-zero)
        total = sum(ratios)
        if total == 0:
            ratios = [1] * cols
            total = cols

        # available width is the viewport width (excludes headers and vertical scrollbar)
        avail = max(0, self.table.viewport().width())

        header = self.table.horizontalHeader()
        header.setMinimumSectionSize(20)
        # ensure interactive mode so setColumnWidth takes effect
        for i in range(cols):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)

        used = 0
        for i in range(cols):
            # compute width, last column gets remainder to avoid rounding gaps
            if i < cols - 1:
                w = int(round(ratios[i] / total * avail))
            else:
                w = max(0, avail - used)
            w = max(20, w)  # enforce a small minimum
            try:
                self.table.setColumnWidth(i, w)
            except Exception:
                # defensive: ignore failures to set column width
                pass
            used += w

    def resizeEvent(self, event):
        # reapply ratios when the widget is resized so columns redistribue correctly
        super().resizeEvent(event)
        if self._column_ratios:
            self._apply_column_ratios()
