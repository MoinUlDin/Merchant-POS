# app/windows/change_password_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from app.services.auth_service_sqlite3 import AuthServiceSQLite3
from app.utils.i18n import t

class ChangePasswordDialog(QDialog):
    def __init__(self, get_lang=lambda: "ur", parent=None):
        super().__init__(parent)
        self.get_lang = get_lang
        self.auth = AuthServiceSQLite3()
        self._build_ui()
        self.update_texts()

    def _build_ui(self):
        self.setModal(True)
        layout = QVBoxLayout()
        self.curr_lbl = QLabel()
        self.curr_input = QLineEdit()
        self.curr_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.curr_lbl); layout.addWidget(self.curr_input)

        self.new_lbl = QLabel()
        self.new_input = QLineEdit()
        self.new_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.new_lbl); layout.addWidget(self.new_input)

        self.confirm_lbl = QLabel()
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_lbl); layout.addWidget(self.confirm_input)

        self.msg = QLabel()
        layout.addWidget(self.msg)

        row = QHBoxLayout()
        row.addStretch()
        self.ok = QPushButton()
        self.ok.clicked.connect(self.on_ok)
        self.cancel = QPushButton()
        self.cancel.clicked.connect(self.reject)
        row.addWidget(self.ok); row.addWidget(self.cancel)
        layout.addLayout(row)

        self.setLayout(layout)

    def update_texts(self):
        lang = self.get_lang()
        self.setWindowTitle(t(lang, "change_password"))
        self.curr_lbl.setText(t(lang, "password_placeholder"))
        self.new_lbl.setText(t(lang, "password_placeholder") + " (new)")
        self.confirm_lbl.setText(t(lang, "password_placeholder") + " (confirm)")
        self.ok.setText("Save")
        self.cancel.setText("Cancel")
        self.msg.setText("")

    def on_ok(self):
        lang = self.get_lang()
        curr = self.curr_input.text() or ""
        new = self.new_input.text() or ""
        conf = self.confirm_input.text() or ""
        if not self.auth.verify_password("Admin", curr):
            self.msg.setText(t(lang, "login_failed")); return
        if new != conf:
            self.msg.setText("Passwords do not match"); return
        if not new:
            self.msg.setText("New password cannot be empty"); return
        self.auth.set_password("Admin", new)
        self.accept()
