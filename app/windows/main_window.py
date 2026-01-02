from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QComboBox, QStackedLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from pathlib import Path

from app.utils.i18n import t
from app.windows.change_password_dialog import ChangePasswordDialog
from app.windows.products_list_screen import ProductsListScreen
from app.windows.product_form_screen import ProductFormScreen


class MainWindow(QMainWindow):
    def __init__(self, urdu_font_family=None):
        super().__init__()
        self.urdu_font_family = urdu_font_family
        self.current_lang = "ur"
        self.init_ui()

    def icon(self, name: str):
        root = Path(__file__).resolve().parents[2] / "resources" / "icons"
        path = root / f"{name}.svg"
        return QIcon(str(path)) if path.exists() else QIcon()

    def init_ui(self):
        self.setWindowTitle(t(self.current_lang, "app_title"))
        self.setMinimumSize(1100, 700)

        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(central)

        # ===== TOP TOOLBAR =====
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 8, 8, 8)

        self.btn_dashboard = QPushButton(t(self.current_lang, "dashboard"))
        self.btn_dashboard.setIcon(self.icon("home"))
        self.btn_dashboard.clicked.connect(lambda: self.switch("dashboard"))

        self.btn_pos = QPushButton(t(self.current_lang, "pos"))
        self.btn_pos.setIcon(self.icon("shopping-cart"))
        self.btn_pos.clicked.connect(lambda: self.switch("pos"))

        self.btn_products = QPushButton(t(self.current_lang, "products"))
        self.btn_products.setIcon(self.icon("box"))
        self.btn_products.clicked.connect(lambda: self.switch("products_list"))

        self.btn_reports = QPushButton(t(self.current_lang, "reports"))
        self.btn_reports.setIcon(self.icon("bar-chart-2"))
        self.btn_reports.clicked.connect(lambda: self.switch("reports"))

        toolbar_layout.addWidget(self.btn_dashboard)
        toolbar_layout.addWidget(self.btn_pos)
        toolbar_layout.addWidget(self.btn_products)
        toolbar_layout.addWidget(self.btn_reports)
        toolbar_layout.addStretch()

        self.btn_change_pw = QPushButton(t(self.current_lang, "change_password"))
        self.btn_change_pw.setIcon(self.icon("key"))
        self.btn_change_pw.clicked.connect(self.open_change_password)
        toolbar_layout.addWidget(self.btn_change_pw)

        self.lang_combo = QComboBox()
        self.lang_combo.addItem("اردو", "ur")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.currentIndexChanged.connect(self.on_lang)
        toolbar_layout.addWidget(self.lang_combo)

        main_layout.addWidget(toolbar)

        # ===== STACKED SCREENS =====
        self.stack = QStackedLayout()
        container = QWidget()
        container.setLayout(self.stack)
        main_layout.addWidget(container)

        # Screens
        self.dashboard_screen = QWidget()
        self.pos_screen = QWidget()
        self.reports_screen = QWidget()

        self.products_list_screen = ProductsListScreen(
            on_add=self.open_add_product,
            on_edit=self.open_edit_product
        )

        self.product_form_screen = ProductFormScreen(
            on_back=lambda: self.switch("products_list")
        )

        self.screens = {
            "dashboard": self.dashboard_screen,
            "pos": self.pos_screen,
            "products_list": self.products_list_screen,
            "product_form": self.product_form_screen,
            "reports": self.reports_screen,
        }

        for screen in self.screens.values():
            self.stack.addWidget(screen)

        self.switch("dashboard")
        self.apply_language()

    def switch(self, key):
        widget = self.screens.get(key)
        if widget:
            self.stack.setCurrentWidget(widget)

    def open_add_product(self):
        self.product_form_screen.load_new()
        self.switch("product_form")

    def open_edit_product(self, product_id):
        self.product_form_screen.load_existing(product_id)
        self.switch("product_form")

    def open_change_password(self):
        dlg = ChangePasswordDialog(get_lang=lambda: self.current_lang, parent=self)
        dlg.exec()

    def on_lang(self):
        self.current_lang = self.lang_combo.currentData()
        self.apply_language()

    def apply_language(self):
        if self.current_lang == "ur":
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            if self.urdu_font_family:
                self.setStyleSheet(
                    f"* {{ font-family: '{self.urdu_font_family}'; letter-spacing: 1.5px; }}"
                )
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            self.setStyleSheet("")

        self.btn_dashboard.setText(t(self.current_lang, "dashboard"))
        self.btn_pos.setText(t(self.current_lang, "pos"))
        self.btn_products.setText(t(self.current_lang, "products"))
        self.btn_reports.setText(t(self.current_lang, "reports"))
        self.btn_change_pw.setText(t(self.current_lang, "change_password"))
