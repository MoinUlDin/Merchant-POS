# app/windows/login_screen.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from app.services.auth_service_sqlite3 import AuthServiceSQLite3
from app.utils.i18n import t
from app.windows.main_window import MainWindow

class LoginScreen(QWidget):
    def __init__(self, urdu_font_family=None):
        super().__init__()
        self.urdu_font_family = urdu_font_family
        self.auth = AuthServiceSQLite3()
        self.lang = "ur"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(t(self.lang, "app_title"))
        layout = QVBoxLayout()
        layout.setContentsMargins(40,40,40,40)

        self.title = QLabel(t(self.lang, "login"))
        self.title.setStyleSheet("font-size:22px; font-weight:600;")
        layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.user_label = QLabel(f"{t(self.lang,'username')}: Admin")
        layout.addWidget(self.user_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText(t(self.lang,'password_placeholder'))
        self.password.returnPressed.connect(self.attempt_login)
        layout.addWidget(self.password)

        self.msg = QLabel("")
        layout.addWidget(self.msg, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn = QPushButton(t(self.lang,'login_button'))
        self.btn.clicked.connect(self.attempt_login)
        layout.addWidget(self.btn, alignment=Qt.AlignmentFlag.AlignCenter)

        if self.urdu_font_family:
            self.setStyleSheet(f"* {{ font-family: '{self.urdu_font_family}'; }}")
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.setLayout(layout)
        self.setMinimumSize(900,600)

    def attempt_login(self):
        pw = self.password.text() or ""
        if self.auth.verify_password("Admin", pw):
            self.mainwin = MainWindow(urdu_font_family=self.urdu_font_family)
            self.mainwin.show()
            self.close()
        else:
            self.msg.setText(t(self.lang, "login_failed"))
            self.password.clear()
            self.password.setFocus()
