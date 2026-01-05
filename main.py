# main.py (root of Kiryana Store)
import sys, os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtCore import QLocale
from app.services.db_sqlite3 import get_connection
from app.services.auth_service_sqlite3 import AuthServiceSQLite3
from app.windows.login_screen import LoginScreen

def resource_path(rel):
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(".")
    return os.path.join(base, rel)

def load_urdu_font():
    path = resource_path("resources/fonts/JameelNoori.ttf")
    if os.path.exists(path):
        _id = QFontDatabase.addApplicationFont(path)
        families = QFontDatabase.applicationFontFamilies(_id)
        if families:
            return families[0]
    return None

def main():
    app = QApplication(sys.argv)
    QLocale.setDefault(QLocale(QLocale.Language.Urdu))

    # ensure DB exists (use init_db.py or call schema here)
    # if DB not created, you should run init_db.py once beforehand.
    conn = get_connection()  # will fail if DB not initialized; run init_db.py first
    auth = AuthServiceSQLite3()
    auth.ensure_default_user("Admin", "admin")

    urdu_font = load_urdu_font()
    if urdu_font:
        font = QFont(urdu_font, 14)
        # 🔹 Increase letter spacing for Urdu
        # AbsoluteSpacing = pixels between glyphs
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.6)
        # Try values between: 1.0 – 2.5 for best look

        app.setFont(font)

    login = LoginScreen(urdu_font_family=urdu_font)
    login.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
