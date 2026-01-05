from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QMessageBox, QSpacerItem
)
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from PyQt6.QtCore import Qt
from app.utils.i18n import t
from ..services.product_service import ProductService


class ProductFormScreen(QWidget):
    def __init__(self, on_back, on_saved=None, get_lang=lambda: "ur"):
        super().__init__()
        self.on_back = on_back
        self.on_saved = on_saved
        self.get_lang = get_lang

        self.product_id = None
        self.product_service = ProductService()

        # validators
        self.price_validator = QDoubleValidator(0.0, 1_000_000_000.0, 2, self)
        self.int_validator = QIntValidator(0, 1_000_000_000, self)

        # build UI and then apply language (so labels are set in one place)
        self._build_ui()
        self.apply_language()
        
    # -----------------------
    # UI construction
    # -----------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(80,20,80,20)
        
        # Top bar (back + title)
        top = QHBoxLayout()
        self.btn_back = QPushButton()
        self.btn_back.setStyleSheet("border-radius: 4px; border: 2px solid rgb(0, 180, 180); padding: 2px")
        self.btn_back.clicked.connect(self.on_back)
        top.addWidget(self.btn_back)

        self.title = QLabel()
        self.title.setStyleSheet("font-size: 22px; font-weight: bold;")
        top.addWidget(self.title)
        top.addStretch()
        layout.addLayout(top)

        # Two-column form area
        cols = QHBoxLayout()
        left_form = QFormLayout()
        left_form.setContentsMargins(50,0,0,0)
        right_form = QFormLayout()
        right_form.setContentsMargins(0,0,50,0)

        # Spacing
        left_form.setHorizontalSpacing(10)
        right_form.setHorizontalSpacing(10)
        left_form.setVerticalSpacing(10)
        right_form.setVerticalSpacing(10)
        
        # Input widgets
        self.name_ur = QLineEdit()
        self.name_en = QLineEdit()
        self.company = QLineEdit()
        self.barcode = QLineEdit()

        self.base_price = QLineEdit()
        self.base_price.setValidator(self.price_validator)
        self.sell_price = QLineEdit()
        self.sell_price.setValidator(self.price_validator)

        self.stock_qty = QLineEdit()
        self.stock_qty.setValidator(self.int_validator)
        self.reorder_threshold = QLineEdit()
        self.reorder_threshold.setValidator(self.int_validator)

        # Create label widgets ONCE and store references
        self.lbl_name_ur = QLabel()
        self.lbl_name_en = QLabel()
        self.lbl_company = QLabel()
        self.lbl_barcode = QLabel()

        self.lbl_prices_title = QLabel()
        self.lbl_base_price = QLabel()
        self.lbl_sell_price = QLabel()
        self.lbl_stock_qty = QLabel()
        self.lbl_reorder_threshold = QLabel()

        # Left column: names / company / barcode
        left_form.addRow(self.lbl_name_ur, self.name_ur)
        left_form.addRow(self.lbl_name_en, self.name_en)
        left_form.addRow(self.lbl_company, self.company)
        left_form.addRow(self.lbl_barcode, self.barcode)

        # Right column: prices and stock
        # put a title row for prices (single widget, label on left)
        right_form.addRow(self.lbl_base_price, self.base_price)
        right_form.addRow(self.lbl_sell_price, self.sell_price)
        right_form.addRow(self.lbl_stock_qty, self.stock_qty)
        right_form.addRow(self.lbl_reorder_threshold, self.reorder_threshold)

        
        cols.addLayout(left_form)
        cols.addLayout(right_form)
        layout.addLayout(cols)

        # Save button
        self.btn_save = QPushButton(t(self.get_lang(), "save_product"))
        
        self.btn_save.clicked.connect(self.save_product)
        layout.addWidget(self.btn_save, alignment=Qt.AlignmentFlag.AlignLeft)

        # Keep form layouts for possible future use
        self._left_form = left_form
        self._right_form = right_form
        self.apply_styles()

    def apply_styles(self):
        # self.btn_save.setStyleSheet('padding: 5px 15px; border: 1px solid rgb(95,99,104); border-radius: 4px')
        pass
    
    # -----------------------
    # Label provider (single source)
    # -----------------------
    def get_label_text(self, key, lang):
        """
        Return the correct label text for the given key and language.
        First tries your i18n function t(lang, key), then falls back to built-in strings.
        """
        fallbacks = {
            "name_ur": ("نام (اردو)", "Name (Urdu)"),
            "name_en": ("نام (انگریزی)", "Name (English)"),
            "company": ("کمپنی", "Company"),
            "barcode": ("بار کوڈ", "Barcode"),
            "base_price": ("قیمت خرید", "Base Price"),
            "sell_price": ("قیمت فروخت", "Sell Price"),
            "stock_qty": ("مقدار", "Stock Quantity"),
            "reorder_threshold": ("کم مقدار", "Reorder Threshold"),
            "back": ("← واپس", "← Back"),
            "new_product": ("نیا پراڈکٹ", "New Product"),
            "edit_product": ("پراڈکٹ میں ترمیم", "Edit Product"),
            "validation_error": ("غلطی", "Validation Error"),
            "info": ("معلومات", "Info"),
            "product_saved": ("محفوظ ہوگیا", "Product saved.")
        }
        ur_text, en_text = fallbacks.get(key, (key, key))
        return ur_text if lang == "ur" else en_text

    # -----------------------
    # Language helpers
    # -----------------------
    def set_get_lang(self, get_lang):
        """Update how this widget obtains the current language."""
        self.get_lang = get_lang

    def apply_language(self):
        """
        Update label texts and input alignment based on current language.
        Does NOT clear QLineEdit contents.
        """
        lang = self.get_lang() if callable(self.get_lang) else "ur"

        # Title/back
        title_key = "new_product" if self.product_id is None else "edit_product"
        self.title.setText(self.get_label_text(title_key, lang))
        self.btn_back.setText(self.get_label_text("back", lang))

        # Update labels
        self.lbl_name_ur.setText(self.get_label_text("name_ur", lang))
        self.lbl_name_en.setText(self.get_label_text("name_en", lang))
        self.lbl_company.setText(self.get_label_text("company", lang))
        self.lbl_barcode.setText(self.get_label_text("barcode", lang))

        self.lbl_base_price.setText(self.get_label_text("base_price", lang))
        self.lbl_sell_price.setText(self.get_label_text("sell_price", lang))
        self.lbl_stock_qty.setText(self.get_label_text("stock_qty", lang))
        self.lbl_reorder_threshold.setText(self.get_label_text("reorder_threshold", lang))

        #save button
        self.btn_save.setText(t(self.get_lang(), 'save_product'))

        # Align text fields for LTR/RTL
        if lang == "ur":
            alignment = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            direction = Qt.LayoutDirection.RightToLeft
            u_direction = Qt.AlignmentFlag.AlignLeft
        else:
            alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            u_direction = Qt.AlignmentFlag.AlignRight
            direction = Qt.LayoutDirection.LeftToRight

        for field in (
            self.name_ur, self.name_en, self.company, self.barcode,
            self.base_price, self.sell_price, self.stock_qty, self.reorder_threshold
        ):
            field.setLayoutDirection(direction)
            if field == self.name_ur:
                field.setAlignment(u_direction)
            else:
                field.setAlignment(alignment)

    # -----------------------
    # Data load / clear
    # -----------------------
    def load_new(self):
        self.product_id = None
        self.clear_all()
        self.apply_language()

    def load_existing(self, product_id):
        self.product_id = product_id
        prod = self.product_service.get(product_id)
        if prod:
            # expected mapping: id, ur_name, en_name, company, barcode, base_price, sell_price, stock_qty, reorder_threshold
            self.name_ur.setText(str(prod[1] or ""))
            self.name_en.setText(str(prod[2] or ""))
            self.company.setText(str(prod[3] or ""))
            self.barcode.setText(str(prod[4] or ""))
            self.base_price.setText(str(prod[5] or ""))
            self.sell_price.setText(str(prod[6] or ""))
            self.stock_qty.setText(str(prod[7] or ""))
            self.reorder_threshold.setText(str(prod[8] or ""))
        self.apply_language()

    def clear_all(self):
        self.name_ur.clear()
        self.name_en.clear()
        self.company.clear()
        self.barcode.clear()
        self.base_price.clear()
        self.sell_price.clear()
        self.stock_qty.clear()
        self.reorder_threshold.clear()

    # -----------------------
    # Messages / validation
    # -----------------------
    def _show_error(self, message, title=None):
        lang = self.get_lang() if callable(self.get_lang) else "ur"
        if not title:
            title = self.get_label_text("validation_error", lang)
        QMessageBox.warning(self, title, message)

    def _show_info(self, message, title=None):
        lang = self.get_lang() if callable(self.get_lang) else "ur"
        if not title:
            title = self.get_label_text("info", lang)
        QMessageBox.information(self, title, message)

    def _validate_and_build(self):
        """
        Validates inputs and returns (True, data) or (False, error_message).
        Rules enforced:
          - at least one name (ur or en)
          - company and barcode required
          - base_price and sell_price: floats > 0, sell > base
          - stock_qty: int >= 0
          - reorder_threshold: int > 0
        """
        lang = self.get_get_lang_safe()
        ur = self.name_ur.text().strip()
        en = self.name_en.text().strip()
        company = self.company.text().strip()
        barcode = self.barcode.text().strip()
        base_price_s = self.base_price.text().strip()
        sell_price_s = self.sell_price.text().strip()
        stock_s = self.stock_qty.text().strip()
        reorder_s = self.reorder_threshold.text().strip()

        if ur == "" and en == "":
            return False, self.get_label_text("name_ur", lang) + " / " + self.get_label_text("name_en", lang) + " " + (
                "درکار ہے" if lang == "ur" else "is required"
            )

        if company == "" or barcode == "":
            return False, self.get_label_text("company", lang) + " & " + self.get_label_text("barcode", lang) + " " + (
                "درکار ہیں" if lang == "ur" else "are required"
            )

        # parse prices
        try:
            base_price = float(base_price_s)
        except Exception:
            return False, self.get_label_text("base_price", lang) + " " + ("درست نہیں" if lang == "ur" else "is invalid")

        try:
            sell_price = float(sell_price_s)
        except Exception:
            return False, self.get_label_text("sell_price", lang) + " " + ("درست نہیں" if lang == "ur" else "is invalid")

        if base_price <= 0 or sell_price <= 0:
            return False, (self.get_label_text("base_price", lang) + " / " + self.get_label_text("sell_price", lang) + " " +
                           ("صفر یا منفی نہیں ہو سکتیں" if lang == "ur" else "must be greater than zero"))

        if sell_price <= base_price:
            return False, self.get_label_text("sell_price", lang) + " ، " + (
                "قیمت خرید سے زیادہ ہونی چاہیے" if lang == "ur" else "must be greater than base price"
            )

        # parse stocks
        try:
            stock_qty = int(stock_s)
        except Exception:
            return False, self.get_label_text("stock_qty", lang) + " " + ("درست نہیں" if lang == "ur" else "is invalid")

        try:
            reorder_threshold = int(reorder_s)
        except Exception:
            return False, self.get_label_text("reorder_threshold", lang) + " " + ("درست نہیں" if lang == "ur" else "is invalid")

        if stock_qty < 0 or reorder_threshold < 0:
            return False, (self.get_label_text("stock_qty", lang) + " / " + self.get_label_text("reorder_threshold", lang) + " " +
                           ("صفر یا منفی نہیں ہو سکتے" if lang == "ur" else "must be zero or greater"))

        if reorder_threshold == 0:
            return False, self.get_label_text("reorder_threshold", lang) + " " + (
                "زیرو نہیں ہو سکتی" if lang == "ur" else "must be greater than zero"
            )

        data = {
            "ur_name": ur,
            "en_name": en,
            "company": company,
            "barcode": barcode,
            "base_price": base_price,
            "sell_price": sell_price,
            "stock_qty": stock_qty,
            "reorder_threshold": reorder_threshold,
        }
        return True, data

    def get_get_lang_safe(self):
        return self.get_lang() if callable(self.get_lang) else "ur"

    # -----------------------
    # Save
    # -----------------------
    def save_product(self):
        ok, payload = self._validate_and_build()
        if not ok:
            self._show_error(payload)
            return

        try:
            if self.product_id is None:
                result = self.product_service.create(data=payload)
                self.clear_all()
            else:
                result = self.product_service.update(self.product_id, data=payload)
                
        except Exception as e:
            self._show_error(str(e))
            return

        # success message
        lang = self.get_get_lang_safe()
        self._show_info(self.get_label_text("product_saved", lang))

        # notify parent to refresh
        if callable(self.on_saved):
            try:
                print("calling on Saved")
                self.on_saved()
            except Exception:
                pass

        # if create returned an id, set it (otherwise leave as-is)
        if self.product_id is None and isinstance(result, int):
            self.product_id = result

        # refresh title text according to language
        self.apply_language()

