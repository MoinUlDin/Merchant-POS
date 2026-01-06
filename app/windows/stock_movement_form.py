# app/windows/stock_movement_form.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from app.services.product_service import ProductService
from app.services.stock_service import StockService
from app.utils.i18n import t


class StockMovementForm(QWidget):
    """
    Form for recording stock movements. Uses StockService methods to update stock.
    Emits movement_recorded(product_id:int, new_stock:float) on success.
    """
    movement_recorded = pyqtSignal(int, float)

    def __init__(self, on_back=None, get_lang=lambda: "ur", urdu_font_family=None):
        super().__init__()
        self.on_back = on_back
        self.get_lang = get_lang
        self.urdu_font_family = urdu_font_family

        self.product_service = ProductService()
        self.stock_service = StockService()

        # currently selected product (None or tuple product row as returned by ProductService.get)
        self.current_product = None

        # validators
        self.qty_validator = QDoubleValidator(0.0, 1_000_000.0, 3, self)
        self.int_validator = QIntValidator(0, 2_000_000_000, self)
        self.cost_validator = QDoubleValidator(0.0, 10_000_000.0, 2, self)

        self._build_ui()
        self.apply_language()
        self.apply_styles()

    # -----------------------
    # UI
    # -----------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(14)

        # Top bar (back + title)
        top = QHBoxLayout()
        self.btn_back = QPushButton()
        self.btn_back.clicked.connect(self._on_back_clicked)
        top.addWidget(self.btn_back)

        self.title = QLabel()
        self.title.setStyleSheet("font-size:18px; font-weight:700;")
        top.addWidget(self.title)
        top.addStretch()
        layout.addLayout(top)

        # Form area (card-like)
        card = QWidget()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 12, 18, 12)
        card_layout.setSpacing(10)

        form_area = QFormLayout()
        form_area.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_area.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        form_area.setHorizontalSpacing(18)
        form_area.setVerticalSpacing(10)

        # Product lookup by barcode or short_code
        self.barcode_field = QLineEdit()
        self.btn_find = QPushButton()
        self.btn_find.clicked.connect(self.on_find_product)
        barcode_h = QHBoxLayout()
        barcode_h.addWidget(self.barcode_field)
        barcode_h.addWidget(self.btn_find)

        self.lbl_product_name = QLabel("—")
        self.lbl_current_stock = QLabel("—")

        # Movement direction and reason
        self.direction = QComboBox()
        # values localized in apply_language()

        self.reason = QComboBox()
        # store canonical keys as itemData in apply_language()

        # quantity and unit
        self.qty = QLineEdit()
        self.qty.setValidator(self.qty_validator)
        self.unit = QLineEdit()  # will default to product.unit if available

        # optional fields
        self.reference_id = QLineEdit()
        self.reference_id.setValidator(self.int_validator)
        self.related_doc = QLineEdit()
        self.cost_total = QLineEdit()
        self.cost_total.setValidator(self.cost_validator)  # rupees float or paisa int accepted
        self.created_by = QLineEdit()
        self.created_by.setPlaceholderText("Admin")

        # Add rows to form
        form_area.addRow(QLabel(self._label("scan_barcode", self.get_lang(), "Barcode/ShortCode")), barcode_h)
        form_area.addRow(QLabel(self._label("product", self.get_lang(), "Product")), self.lbl_product_name)
        form_area.addRow(QLabel(self._label("current_stock", self.get_lang(), "Current Stock")), self.lbl_current_stock)
        form_area.addRow(QLabel(self._label("direction", self.get_lang(), "Direction")), self.direction)
        form_area.addRow(QLabel(self._label("reason", self.get_lang(), "Reason")), self.reason)
        form_area.addRow(QLabel(self._label("quantity", self.get_lang(), "Quantity")), self.qty)
        form_area.addRow(QLabel(self._label("unit", self.get_lang(), "Unit")), self.unit)
        form_area.addRow(QLabel(self._label("reference_id", self.get_lang(), "Reference ID")), self.reference_id)
        form_area.addRow(QLabel(self._label("related_doc", self.get_lang(), "Related Doc")), self.related_doc)
        form_area.addRow(QLabel(self._label("cost_total", self.get_lang(), "Cost (₹)")), self.cost_total)
        form_area.addRow(QLabel(self._label("created_by", self.get_lang(), "Created By")), self.created_by)

        card_layout.addLayout(form_area)

        # Save / Clear buttons
        btns = QHBoxLayout()
        btns.addStretch()
        self.btn_clear = QPushButton()
        self.btn_save = QPushButton()
        btns.addWidget(self.btn_clear)
        btns.addWidget(self.btn_save)
        card_layout.addLayout(btns)

        layout.addWidget(card)

        # wire up simple actions
        self.btn_save.clicked.connect(self.on_save)
        self.btn_clear.clicked.connect(self.clear_form)
        self.barcode_field.returnPressed.connect(self.on_find_product)
        self.btn_find.clicked.connect(self.on_find_product)

        # keep references
        self._form = form_area

    # -----------------------
    # Language & styling
    # -----------------------
    def apply_language(self):
        lang = self.get_lang() if callable(self.get_lang) else "ur"

        # top controls
        self.btn_back.setText(self._label("back", lang, "← Back"))
        self.title.setText(self._label("stock_movement", lang, "Stock Movement"))

        # form labels / buttons
        self.btn_find.setText(self._label("find", lang, "Find"))
        self.btn_save.setText(self._label("save", lang, "Save"))
        self.btn_clear.setText(self._label("clear", lang, "Clear"))

        # direction localized (replace current values)
        self.direction.clear()
        if lang == "ur":
            self.direction.addItems(["آمد", "جانا"])  # Incoming, Outgoing
        else:
            self.direction.addItems(["Incoming", "Outgoing"])

        # reason localization: underlying keys stored as itemData
        reason_keys = ["purchase_receipt", "sale", "manual_adjust", "return", "inventory_correction"]
        self.reason.clear()
        if lang == "ur":
            labels = ["خرید", "فروخت", "دستی ایڈجسٹ", "واپسی", "انوینٹری درستگی"]
        else:
            labels = ["Purchase Receipt", "Sale", "Manual Adjust", "Return", "Inventory Correction"]
        for rlabel, rkey in zip(labels, reason_keys):
            self.reason.addItem(rlabel, rkey)

        # placeholders / field hints
        self.barcode_field.setPlaceholderText(self._label("scan_barcode_placeholder", lang, "Scan or type barcode/shortcode"))
        self.qty.setPlaceholderText("0.00")
        self.unit.setPlaceholderText(self._label("unit_placeholder", lang, "unit (e.g., kg, pcs)"))
        self.reference_id.setPlaceholderText(self._label("optional", lang, "optional"))
        self.related_doc.setPlaceholderText(self._label("optional", lang, "optional"))
        self.cost_total.setPlaceholderText(self._label("cost_rupees", lang, "Rs (e.g. 1200.50)"))
        self.created_by.setText(self._label("admin_username", lang, "Admin"))

        # style font family if provided (RTL handled by parent app)
        if self.urdu_font_family:
            self.setStyleSheet(f"* {{ font-family: '{self.urdu_font_family}'; }}")

    def _label(self, key, lang, fallback):
        try:
            return t(lang, key)
        except Exception:
            return fallback

    # -----------------------
    # Product lookup helpers
    # -----------------------
    def on_find_product(self):
        """Find product by barcode or short_code, then populate product name and unit/stock."""
        code = (self.barcode_field.text() or "").strip()
        if code == "":
            QMessageBox.warning(self, self._label("validation_error", self.get_lang(), "Validation Error"),
                                self._label("barcode_required", self.get_lang(), "Please enter barcode or short code"))
            return

        # try exact barcode match first
        prod = self.product_service.find_by_barcode(code)
        if prod:
            product_id = prod[0]
            prod_full = self.product_service.get(product_id)
        else:
            rows = self.product_service.search(code, limit=5)
            prod_full = rows[0] if rows else None

        if not prod_full:
            QMessageBox.information(self, self._label("not_found", self.get_lang(), "Not Found"),
                                    self._label("product_not_found", self.get_lang(), "Product not found"))
            self.current_product = None
            self.lbl_product_name.setText("—")
            self.lbl_current_stock.setText("—")
            return

        # product tuple expected as in ProductService.get()
        self.current_product = prod_full
        lang = self.get_lang() or "ur"
        ur_name = (prod_full[2] or "").strip() if len(prod_full) > 2 else ""
        en_name = (prod_full[3] or "").strip() if len(prod_full) > 3 else ""
        display_name = en_name if (lang == "en" and en_name) else ur_name or en_name or prod_full[1] or f"#{prod_full[0]}"
        self.lbl_product_name.setText(display_name)

        # set current stock label and default unit (use safe indexes)
        try:
            stock_val = float(prod_full[8] or 0.0)
        except Exception:
            stock_val = 0.0
        self.lbl_current_stock.setText(str(stock_val))

        unit = prod_full[11] if len(prod_full) > 11 else "kg"
        self.unit.setText(unit)

    # -----------------------
    # Save movement
    # -----------------------
    def on_save(self):
        lang = self.get_lang() if callable(self.get_lang) else "ur"

        if not self.current_product:
            QMessageBox.warning(self, self._label("validation_error", lang, "Validation Error"),
                                self._label("select_product_first", lang, "Please select a product first"))
            return

        qty_text = (self.qty.text() or "").strip()
        if qty_text == "":
            QMessageBox.warning(self, self._label("validation_error", lang, "Validation Error"),
                                self._label("qty_required", lang, "Please enter quantity"))
            return

        try:
            qty_val = float(qty_text)
        except Exception:
            QMessageBox.warning(self, self._label("validation_error", lang, "Validation Error"),
                                self._label("qty_invalid", lang, "Quantity is invalid"))
            return

        # direction: incoming adds, outgoing subtracts
        direction_index = self.direction.currentIndex()
        is_incoming = (direction_index == 0)  # 0=Incoming, 1=Outgoing

        reason_key = self.reason.currentData() or self.reason.currentText()

        # optional numeric fields
        ref_id_text = (self.reference_id.text() or "").strip()
        ref_id = int(ref_id_text) if ref_id_text != "" else None
        related_doc = (self.related_doc.text() or "").strip()
        cost_text = (self.cost_total.text() or "").strip()
        cost_val = None
        if cost_text != "":
            try:
                cost_val = float(cost_text)
            except Exception:
                QMessageBox.warning(self, self._label("validation_error", lang, "Validation Error"),
                                    self._label("cost_invalid", lang, "Cost is invalid"))
                return

        created_by = (self.created_by.text() or "Admin").strip()
        product_id = int(self.current_product[0])

        # Decide which stock service method to call:
        # - If purchase_receipt & incoming and qty is integer -> receive_packs(num_packs)
        # - If sale & outgoing -> consume_for_sale(abs(qty))
        # - Otherwise call record_movement with signed qty
        try:
            new_stock = None
            if reason_key == "purchase_receipt" and is_incoming:
                # Prefer receive_packs when cashier entered number of packs
                if float(qty_val).is_integer():
                    num_packs = max(0, int(qty_val))
                    if num_packs == 0:
                        raise ValueError("Number of packs must be >= 1")
                    new_stock = self.stock_service.receive_packs(
                        product_id=product_id,
                        num_packs=num_packs,
                        reason=reason_key,
                        cost_total=cost_val,
                        created_by=created_by,
                        reference_id=ref_id
                    )
                else:
                    # if qty is fractional, fallback to record_movement using base-unit qty
                    new_stock = self.stock_service.record_movement(
                        product_id=product_id,
                        qty=abs(qty_val),
                        reason=reason_key,
                        reference_id=ref_id,
                        related_doc=related_doc if related_doc != "" else None,
                        unit=self.unit.text() or None,
                        cost_total=cost_val,
                        created_by=created_by
                    )
            elif reason_key == "sale" and not is_incoming:
                # sale -> consume stock (consume_for_sale expects a positive qty; it records negative internally)
                new_stock = self.stock_service.consume_for_sale(
                    product_id=product_id,
                    qty=abs(qty_val),
                    sale_id=ref_id,
                    created_by=created_by
                )
            else:
                # general movement: sign according to direction
                movement_qty = abs(qty_val) if is_incoming else -abs(qty_val)
                new_stock = self.stock_service.record_movement(
                    product_id=product_id,
                    qty=movement_qty,
                    reason=reason_key,
                    reference_id=ref_id,
                    related_doc=related_doc if related_doc != "" else None,
                    unit=self.unit.text() or None,
                    cost_total=cost_val,
                    created_by=created_by
                )
        except Exception as e:
            QMessageBox.critical(self, self._label("error", lang, "Error"), str(e))
            return

        # success
        QMessageBox.information(self, self._label("info", lang, "Info"),
                                self._label("movement_saved", lang, f"Movement saved. New stock: {new_stock}"))

        # update display of current stock
        self.lbl_current_stock.setText(str(new_stock))

        # emit signal so parent can refresh lists, etc.
        try:
            self.movement_recorded.emit(product_id, float(new_stock))
        except Exception:
            pass

        # keep product selected but clear quantities/optional fields
        self.qty.clear()
        self.reference_id.clear()
        self.related_doc.clear()
        self.cost_total.clear()

    # -----------------------
    # Helpers
    # -----------------------
    def clear_form(self):
        self.barcode_field.clear()
        self.lbl_product_name.setText("—")
        self.lbl_current_stock.setText("—")
        self.current_product = None
        self.qty.clear()
        self.unit.clear()
        self.reference_id.clear()
        self.related_doc.clear()
        self.cost_total.clear()
        self.created_by.setText(self._label("admin_username", self.get_lang(), "Admin"))

    def load_new(self):
        """
        Prepare the form for a new movement.
        """
        self.clear_form()
        try:
            self.apply_language()
        except Exception:
            pass
        try:
            self.barcode_field.setFocus()
        except Exception:
            pass

    def _on_back_clicked(self):
        if callable(self.on_back):
            try:
                self.on_back()
            except Exception:
                pass

    # -----------------------
    # Styling
    # -----------------------
    def apply_styles(self):
        # modern card-like look and clear controls
        self.setStyleSheet("""
        QWidget {
            background: transparent;
        }
        QWidget > QWidget { /* card container inside main layout */
            background: #ffffff;
            border: 1px solid #e6e9ee;
            border-radius: 8px;
        }
        QLabel {
            font-size: 14px;
        }
        QLineEdit, QComboBox {
            
            border: 1px solid #d6dbe6;
            border-radius: 6px;
            min-height: 30px;
            font-size: 14px;
        }
        QPushButton {
            padding: 8px 14px;
            border-radius: 6px;
            background: #2b8be6;
            color: white;
            border: none;
            font-weight: 600;
            min-height: 34px;
        }
        QPushButton:disabled {
            background: #bcd7fb;
        }
        QPushButton[objectName="secondary"] {
            background: #f3f5f8;
            color: #333;
            border: 1px solid #e6e9ee;
        }
        """)
        # mark clear button as secondary for style (objectName selector)
        try:
            self.btn_clear.setObjectName("secondary")
        except Exception:
            pass

