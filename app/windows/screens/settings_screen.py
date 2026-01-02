# app/windows/screens/settings_screen.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from app.utils.i18n import t

class SettingsScreen(QWidget):
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
        layout.addWidget(QLabel("Settings area (printer, backup, simulator) will be added later."))
        self.setLayout(layout)

    def update_texts(self):
        self.title.setText(t(self.get_lang(), "settings_title"))
