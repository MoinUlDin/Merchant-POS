from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFormLayout
)
from app.utils.i18n import t
from ..services.product_service import ProductService


class ProductFormScreen(QWidget):
    def __init__(self, on_back, on_saved=None):
        super().__init__()
        self.on_back = on_back
        self.on_saved = on_saved   # callback to notify parent (e.g. ProductsListScreen) to refresh
        self.product_id = None
        self.product_service = ProductService()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        btn_back = QPushButton("← واپس")
        btn_back.clicked.connect(self.on_back)
        top.addWidget(btn_back)

        self.title = QLabel("نیا پراڈکٹ")
        self.title.setStyleSheet("font-size: 22px; font-weight: bold;")
        top.addWidget(self.title)
        top.addStretch()

        layout.addLayout(top)

        form = QFormLayout()

        self.name_ur = QLineEdit()
        self.name_en = QLineEdit()
        self.company = QLineEdit()
        self.barcode = QLineEdit()
        self.base_price = QLineEdit()
        self.sell_price = QLineEdit()
        self.stock_qty = QLineEdit()
        self.reorder_threshold = QLineEdit()

        form.addRow("نام (اردو)", self.name_ur)
        form.addRow("نام (English)", self.name_en)
        form.addRow("کمپنی", self.company)
        form.addRow("بار کوڈ", self.barcode)
        form.addRow("قیمت خرید", self.base_price)
        form.addRow("قیمت فروخت", self.sell_price)
        form.addRow("مقدار", self.stock_qty)
        form.addRow("کم مقدار", self.reorder_threshold)

        layout.addLayout(form)

        btn_save = QPushButton("💾 محفوظ کریں")
        btn_save.clicked.connect(self.save_product)
        layout.addWidget(btn_save)

    def load_new(self):
        self.product_id = None
        self.title.setText("نیا پراڈکٹ")
        self.clear_all()

    def load_existing(self, product_id):
        self.product_id = product_id
        self.title.setText("پراڈکٹ میں ترمیم")
        # load product from DB
        prod = self.product_service.get(product_id)
        if prod:
            # prod is a tuple with same columns as SELECT *
            # adapt to your table structure; example:
            # id, ur_name, en_name, company, barcode, base_price, sell_price, stock_qty, reorder_threshold, created_at, ...
            self.name_ur.setText(str(prod[1] or ""))
            self.name_en.setText(str(prod[2] or ""))
            self.company.setText(str(prod[3] or ""))
            self.barcode.setText(str(prod[4] or ""))
            self.base_price.setText(str(prod[5] or ""))
            self.sell_price.setText(str(prod[6] or ""))
            self.stock_qty.setText(str(prod[7] or ""))
            self.reorder_threshold.setText(str(prod[8] or ""))

    def clear_all(self):
        self.name_ur.clear()
        self.name_en.clear()
        self.company.clear()
        self.barcode.clear()
        self.base_price.clear()
        self.sell_price.clear()
        self.stock_qty.clear()
        self.reorder_threshold.clear()

    def save_product(self):
        uname = self.name_ur.text().strip()
        ename = self.name_en.text().strip()
        company = self.company.text().strip()
        barcode = self.barcode.text().strip()
        bprice = self.base_price.text().strip()
        sprice = self.sell_price.text().strip()
        qty = self.stock_qty.text().strip()
        rth = self.reorder_threshold.text().strip()

        # basic validation
        if uname == '' or company == '' or barcode == '' or bprice == '' or sprice == '' or qty == '' or rth == '':
            # you may want to show a message box here instead of silent return
            print("validation failed - missing fields")
            return

        data = {
            "ur_name": uname,
            "en_name": ename,
            "company": company,
            "barcode": barcode,
            "base_price": bprice,
            "sell_price": sprice,
            "stock_qty": qty,
            "reorder_threshold": rth,
        }

        if self.product_id is None:
            result = self.product_service.create(data=data)
        else:
            result = self.product_service.update(self.product_id, data=data)

        if result is not None:
            self.clear_all()
            # notify parent to refresh list
            if callable(self.on_saved):
                self.on_saved()
