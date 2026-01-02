# app/windows/screens/dashboard_screen.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from app.utils.i18n import t

class DashboardScreen(QWidget):
    def __init__(self, get_lang=lambda: "ur", parent=None):
        super().__init__(parent)
        self.get_lang = get_lang
        self._build_ui()
        self.update_texts()

    def _build_ui(self):
        layout = QVBoxLayout()
        self.title = QLabel()
        self.title.setStyleSheet("font-size:18px; font-weight:600;")
        layout.addWidget(self.title)
        self.info = QLabel("Dashboard content (sales summary, alerts) will go here.")
        layout.addWidget(self.info)
        self.setLayout(layout)

    def update_texts(self):
        lang = self.get_lang()
        self.title.setText(t(lang, "dashboard_title"))
