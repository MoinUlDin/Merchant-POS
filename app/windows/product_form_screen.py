# app/windows/product_form_screen.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QMessageBox, QComboBox, QCheckBox, QSizePolicy
)
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from PyQt6.QtCore import Qt
from app.utils.i18n import t
from ..services.product_service import ProductService


class ProductFormScreen(QWidget):
    """
    Modern, two-column product form wired to ProductService.

    New fields supported:
      - short_code
      - category (combo if available)
      - unit (combo: kg, gram, ltr, ml, pcs)
      - custom_packing (checkbox)
      - packing_size (numeric)
      - supply_pack_qty (numeric)
      - base_price (rupees, shown as float)
      - sell_price (rupees)
      - stock_qty (float)
      - reorder_threshold (float)
    """

    UNITS = [("kg", "kg"), ("gram", "gram"), ("ltr", "ltr"), ("ml", "ml"), ("pcs", "pcs")]

    def __init__(self, on_back, on_saved=None, get_lang=lambda: "ur"):
        super().__init__()
        self.on_back = on_back
        self.on_saved = on_saved
        self.get_lang = get_lang

        self.product_id = None
        self.product_service = ProductService()

        # validators
        self.price_validator = QDoubleValidator(0.0, 1_000_000_000.0, 2, self)
        self.float_validator = QDoubleValidator(-1_000_000_000.0, 1_000_000_000.0, 3, self)
        self.int_validator = QIntValidator(0, 1_000_000_000, self)

        # build UI and then apply language (so labels are set in one place)
        self._build_ui()
        self.apply_language()
        # try populating categories (if service exposes them)
        self._load_categories()

    # -----------------------
    # UI construction
    # -----------------------
    def _build_ui(self):
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 18, 48, 18)
        layout.setSpacing(12)

        # Top bar (back + title)
        top = QHBoxLayout()
        self.btn_back = QPushButton()
        self.btn_back.setStyleSheet(
            "border-radius: 6px; border: 1px solid rgba(0,0,0,0.08); padding: 6px 10px;"
        )
        self.btn_back.clicked.connect(self.on_back)
        top.addWidget(self.btn_back, alignment=Qt.AlignmentFlag.AlignLeft)

        self.title = QLabel()
        self.title.setStyleSheet("font-size: 20px; font-weight: 700; padding-left: 8px;")
        top.addWidget(self.title)
        top.addStretch()
        layout.addLayout(top)

        # two-column form
        cols = QHBoxLayout()
        cols.setSpacing(12)

        left_form = QFormLayout()
        left_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        right_form = QFormLayout()
        right_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # --- Left widgets ---
        self.short_code = QLineEdit()
        self.name_ur = QLineEdit()
        self.name_en = QLineEdit()
        self.company = QLineEdit()
        self.barcode = QLineEdit()

        # labels
        self.lbl_short_code = QLabel()
        self.lbl_name_ur = QLabel()
        self.lbl_name_en = QLabel()
        self.lbl_company = QLabel()
        self.lbl_barcode = QLabel()


        # --- Right widgets ---
        self.base_price = QLineEdit(); self.base_price.setValidator(self.price_validator)
        self.sell_price = QLineEdit(); self.sell_price.setValidator(self.price_validator)
        self.stock_qty = QLineEdit(); self.stock_qty.setValidator(self.float_validator)
        self.reorder_threshold = QLineEdit(); self.reorder_threshold.setValidator(self.float_validator)

        # new fields
        self.category_cb = QComboBox()
        self.unit_cb = QComboBox()
        for value, label in self.UNITS:
            self.unit_cb.addItem(label, value)

        self.custom_packing = QCheckBox()
        self.packing_size = QLineEdit(); self.packing_size.setValidator(self.float_validator)
        self.supply_pack_qty = QLineEdit(); self.supply_pack_qty.setValidator(self.float_validator)

        # right labels
        self.lbl_base_price = QLabel()
        self.lbl_sell_price = QLabel()
        self.lbl_stock_qty = QLabel()
        self.lbl_reorder_threshold = QLabel()
        self.lbl_category = QLabel()
        self.lbl_unit = QLabel()
        self.lbl_custom_packing = QLabel()
        self.lbl_packing_size = QLabel()
        self.lbl_supply_pack_qty = QLabel()

        
        left_form.addRow(self.lbl_short_code, self.short_code)
        left_form.addRow(self.lbl_name_ur, self.name_ur)
        left_form.addRow(self.lbl_name_en, self.name_en)
        left_form.addRow(self.lbl_company, self.company)
        left_form.addRow(self.lbl_barcode, self.barcode)
        left_form.addRow(self.lbl_category, self.category_cb)
        left_form.addRow(self.lbl_unit, self.unit_cb)
        
        # arrange right form
        right_form.addRow(self.lbl_custom_packing, self.custom_packing)
        right_form.addRow(self.lbl_packing_size, self.packing_size)
        right_form.addRow(self.lbl_supply_pack_qty, self.supply_pack_qty)
        right_form.addRow(self.lbl_base_price, self.base_price)
        right_form.addRow(self.lbl_sell_price, self.sell_price)
        right_form.addRow(self.lbl_stock_qty, self.stock_qty)
        right_form.addRow(self.lbl_reorder_threshold, self.reorder_threshold)

        cols.addLayout(left_form, stretch=2)
        cols.addLayout(right_form, stretch=2)
        layout.addLayout(cols)

        # Save button row
        actions = QHBoxLayout()
        self.btn_save = QPushButton(t(self.get_lang(), "save_product"))
        self.btn_save.setStyleSheet(
            "padding: 8px 18px; border-radius: 6px; background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #06b6d4, stop:1 #0ea5a4); color: white; font-weight:600;"
        )
        self.btn_save.clicked.connect(self.save_product)
        actions.addWidget(self.btn_save, alignment=Qt.AlignmentFlag.AlignLeft)

        # spacer + optional extra actions
        actions.addStretch()
        layout.addLayout(actions)

        # store layouts (for later use)
        self._left_form = left_form
        self._right_form = right_form

    # -----------------------
    # Category loading
    # -----------------------
    def _load_categories(self):
        """
        Attempts to load categories from product_service.list_categories() if available.
        Falls back to empty combobox.
        """
        try:
            if hasattr(self.product_service, "list_categories"):
                cats = self.product_service.list_categories()
                # Expecting iterable of (id, name) or dicts; handle a few shapes
                self.category_cb.clear()
                for c in cats:
                    if isinstance(c, (list, tuple)) and len(c) >= 2:
                        self.category_cb.addItem(str(c[1]), c[0])
                    elif isinstance(c, dict) and "id" in c and "name" in c:
                        self.category_cb.addItem(c["name"], c["id"])
                    else:
                        # generic string
                        self.category_cb.addItem(str(c))
            else:
                # leave category combo empty (user can type later if desired)
                self.category_cb.clear()
                self.category_cb.addItem("", None)
        except Exception:
            # ignore errors; ensure combo exists
            self.category_cb.clear()
            self.category_cb.addItem("", None)

    # -----------------------
    # Label provider (single source)
    # -----------------------
    def get_label_text(self, key, lang):
        fallbacks = {
            "short_code": ("شارٹ کوڈ", "Short code"),
            "name_ur": ("نام (اردو)", "Name (Urdu)"),
            "name_en": ("نام (انگریزی)", "Name (English)"),
            "company": ("کمپنی", "Company"),
            "barcode": ("بار کوڈ", "Barcode"),
            "base_price": ("قیمت خرید", "Base Price (Rs)"),
            "sell_price": ("قیمت فروخت ", "Sell Price (Rs)"),
            "stock_qty": ("اسٹاک (بنیادی اکائی)", "Stock (base unit)"),
            "reorder_threshold": ("کم مقدار", "Reorder Threshold"),
            "category": ("زمرہ", "Category"),
            "unit": ("یونٹ", "Unit"),
            "custom_packing": ("کسٹم پیکنگ قابل", "Custom packing"),
            "packing_size": ("پیکنگ سائز", "Packing size (in unit)"),
            "supply_pack_qty": ("سپلائی پیک سائز", "Supply pack (units)"),
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
        self.get_lang = get_lang

    def apply_language(self):
        lang = self.get_lang() if callable(self.get_lang) else "ur"

        # Title/back
        title_key = "new_product" if self.product_id is None else "edit_product"
        self.title.setText(self.get_label_text(title_key, lang))
        self.btn_back.setText(self.get_label_text("back", lang))

        # Update labels
        self.lbl_short_code.setText(self.get_label_text("short_code", lang))
        self.lbl_name_ur.setText(self.get_label_text("name_ur", lang))
        self.lbl_name_en.setText(self.get_label_text("name_en", lang))
        self.lbl_company.setText(self.get_label_text("company", lang))
        self.lbl_barcode.setText(self.get_label_text("barcode", lang))

        self.lbl_base_price.setText(self.get_label_text("base_price", lang))
        self.lbl_sell_price.setText(self.get_label_text("sell_price", lang))
        self.lbl_stock_qty.setText(self.get_label_text("stock_qty", lang))
        self.lbl_reorder_threshold.setText(self.get_label_text("reorder_threshold", lang))

        self.lbl_category.setText(self.get_label_text("category", lang))
        self.lbl_unit.setText(self.get_label_text("unit", lang))
        self.lbl_custom_packing.setText(self.get_label_text("custom_packing", lang))
        self.lbl_packing_size.setText(self.get_label_text("packing_size", lang))
        self.lbl_supply_pack_qty.setText(self.get_label_text("supply_pack_qty", lang))

        self.btn_save.setText(t(self.get_lang(), "save_product"))

        # placeholders and small UX tips
        self.short_code.setPlaceholderText("SUGR-01")
        self.name_ur.setPlaceholderText(self.get_label_text("name_ur", lang))
        self.name_en.setPlaceholderText(self.get_label_text("name_en", lang))
        self.company.setPlaceholderText(self.get_label_text("company", lang))
        self.barcode.setPlaceholderText(self.get_label_text("barcode", lang))

        self.base_price.setPlaceholderText("0.00")
        self.sell_price.setPlaceholderText("0.00")
        self.packing_size.setPlaceholderText("e.g. 1 or 0.5")
        self.supply_pack_qty.setPlaceholderText("e.g. 50 (kg per bag) or 12 (bottles per pack)")
        self.stock_qty.setPlaceholderText("e.g. 142.0")
        self.reorder_threshold.setPlaceholderText("e.g. 10.0")

        # Align text fields for LTR/RTL
        if lang == "ur":
            direction = Qt.LayoutDirection.RightToLeft
            text_align = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        else:
            direction = Qt.LayoutDirection.LeftToRight
            text_align = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        for field in (
            self.short_code, self.name_ur, self.name_en, self.company, self.barcode,
            self.base_price, self.sell_price, self.packing_size, self.supply_pack_qty,
            self.stock_qty, self.reorder_threshold
        ):
            field.setLayoutDirection(direction)
            field.setAlignment(text_align)

        # checkbox alignment handled automatically

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
            # expected mapping:
            # id, short_code, ur_name, en_name, company, barcode,
            # base_price (paisa), sell_price (paisa), stock_qty, reorder_threshold,
            # category_id, unit, custom_packing, packing_size, supply_pack_qty, created_at, updated_at
            # Defensive indexing
            self.short_code.setText(str(prod[1] or ""))
            self.name_ur.setText(str(prod[2] or ""))
            self.name_en.setText(str(prod[3] or ""))
            self.company.setText(str(prod[4] or ""))
            self.barcode.setText(str(prod[5] or ""))

            # convert paisa -> rupees for display
            try:
                base_paisa = int(prod[6]) if prod[6] is not None else 0
                sell_paisa = int(prod[7]) if prod[7] is not None else 0
                self.base_price.setText(f"{base_paisa/100:.2f}")
                self.sell_price.setText(f"{sell_paisa/100:.2f}")
            except Exception:
                self.base_price.setText(str(prod[6] or ""))
                self.sell_price.setText(str(prod[7] or ""))

            self.stock_qty.setText(str(prod[8] or "0"))
            self.reorder_threshold.setText(str(prod[9] or "0"))

            # category: select if present
            cat_id = prod[10]
            if cat_id is not None:
                idx = self._find_combo_index_by_data(self.category_cb, cat_id)
                if idx >= 0:
                    self.category_cb.setCurrentIndex(idx)

            # unit
            unit = prod[11] or "kg"
            uidx = self.unit_cb.findData(unit)
            if uidx >= 0:
                self.unit_cb.setCurrentIndex(uidx)

            # custom_packing, packing_size, supply_pack_qty
            self.custom_packing.setChecked(bool(prod[12]))
            self.packing_size.setText(str(prod[13] or ""))
            self.supply_pack_qty.setText(str(prod[14] or ""))

        self.apply_language()

    def clear_all(self):
        self.short_code.clear()
        self.name_ur.clear()
        self.name_en.clear()
        self.company.clear()
        self.barcode.clear()
        self.base_price.clear()
        self.sell_price.clear()
        self.stock_qty.clear()
        self.reorder_threshold.clear()
        self.packing_size.clear()
        self.supply_pack_qty.clear()
        self.custom_packing.setChecked(False)
        if self.category_cb.count():
            self.category_cb.setCurrentIndex(0)
        self.unit_cb.setCurrentIndex(0)

    # -----------------------
    # Utilities
    # -----------------------
    def _find_combo_index_by_data(self, combo: QComboBox, data):
        for i in range(combo.count()):
            if combo.itemData(i) == data or combo.itemText(i) == str(data):
                return i
        return -1

    def _show_error(self, message, title=None):
        lang = self.get_get_lang_safe()
        if not title:
            title = self.get_label_text("validation_error", lang)
        QMessageBox.warning(self, title, message)

    def _show_info(self, message, title=None):
        lang = self.get_get_lang_safe()
        if not title:
            title = self.get_label_text("info", lang)
        QMessageBox.information(self, title, message)

    def _validate_and_build(self):
        """
        Validate inputs and build payload dictionary as expected by ProductService.create/update.
        Prices are returned in rupees as floats (ProductService will convert to paisa).
        """
        lang = self.get_get_lang_safe()
        ur = self.name_ur.text().strip()
        en = self.name_en.text().strip()
        company = self.company.text().strip()
        barcode = self.barcode.text().strip()
        short_code = self.short_code.text().strip()

        # parse numeric fields
        try:
            base_price = float(self.base_price.text().strip())
        except Exception:
            return False, self.get_label_text("base_price", lang) + " " + ("درست نہیں" if lang == "ur" else "is invalid")

        try:
            sell_price = float(self.sell_price.text().strip())
        except Exception:
            return False, self.get_label_text("sell_price", lang) + " " + ("درست نہیں" if lang == "ur" else "is invalid")

        if base_price < 0 or sell_price < 0:
            return False, (self.get_label_text("base_price", lang) + " / " + self.get_label_text("sell_price", lang) + " " +
                           ("صفر یا منفی نہیں ہو سکتیں" if lang == "ur" else "must be zero or greater"))

        # optional rule: sell_price should usually be >= base_price, but we allow override with warning
        if sell_price < base_price:
            # allow but warn; treat as valid
            pass

        # stock and reorder (allow floats)
        try:
            stock_qty = float(self.stock_qty.text().strip() or 0.0)
        except Exception:
            return False, self.get_label_text("stock_qty", lang) + " " + ("درست نہیں" if lang == "ur" else "is invalid")

        try:
            reorder_threshold = float(self.reorder_threshold.text().strip() or 0.0)
        except Exception:
            return False, self.get_label_text("reorder_threshold", lang) + " " + ("درست نہیں" if lang == "ur" else "is invalid")

        # packing related
        try:
            packing_size = float(self.packing_size.text().strip()) if self.packing_size.text().strip() != "" else None
        except Exception:
            return False, self.get_label_text("packing_size", lang) + " " + ("درست نہیں" if lang == "ur" else "is invalid")

        try:
            supply_pack_qty = float(self.supply_pack_qty.text().strip() or 1.0)
        except Exception:
            return False, self.get_label_text("supply_pack_qty", lang) + " " + ("درست نہیں" if lang == "ur" else "is invalid")

        category_id = None
        if self.category_cb.count():
            data = self.category_cb.currentData()
            category_id = data if data is not None else None

        unit = self.unit_cb.currentData() or self.unit_cb.currentText()
        custom_packing = 1 if self.custom_packing.isChecked() else 0

        # validation: at least one name
        if ur == "" and en == "":
            return False, self.get_label_text("name_ur", lang) + " / " + self.get_label_text("name_en", lang) + " " + (
                "درکار ہے" if lang == "ur" else "is required"
            )

        # company and barcode remain required in your older rules; keep them required
        if company == "" or barcode == "":
            return False, self.get_label_text("company", lang) + " & " + self.get_label_text("barcode", lang) + " " + (
                "درکار ہیں" if lang == "ur" else "are required"
            )

        payload = {
            "short_code": short_code or None,
            "ur_name": ur,
            "en_name": en,
            "company": company,
            "barcode": barcode,
            "base_price": base_price,      # rupees float; ProductService will convert
            "sell_price": sell_price,
            "stock_qty": stock_qty,
            "reorder_threshold": reorder_threshold,
            "category_id": category_id,
            "unit": unit,
            "custom_packing": custom_packing,
            "packing_size": packing_size,
            "supply_pack_qty": supply_pack_qty,
        }
        return True, payload

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
                # clear form for new entry
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
                # call the provided callback; many callers expect refresh_products()
                self.on_saved()
            except Exception:
                pass

        # if create returned an id, set it (otherwise leave as-is)
        if self.product_id is None and isinstance(result, int):
            self.product_id = result

        # refresh title text according to language
        self.apply_language()
