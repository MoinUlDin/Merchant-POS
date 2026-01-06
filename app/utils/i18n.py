# app/utils/i18n.py
TRANSLATIONS = {
    "en": {
        "app_title":"Kiryana Store POS",
        "login":"Login",
        "username":"Username",
        "password_placeholder":"Enter password",
        "login_button":"Login",
        "login_failed":"Incorrect password",
        "dashboard":"Dashboard",
        "pos":"Point of Sale",
        "products":"Products",
        "reports":"Reports",
        "settings":"Settings",
        "change_password":"Change Password",
        "save_product": "Save",
        "add_product": "New Product",
        "stock_reorder": "Stock Reorder",
    },
    "ur":{
        "app_title":"معین کریانہ اسٹور",
        "login":"لاگ ان",
        "username":"صارف نام",
        "password_placeholder":"پاس ورڈ درج کریں",
        "login_button":"لاگ ان",
        "login_failed":"پاس ورڈ غلط ہے",
        "dashboard":"ڈیش بورڈ",
        "pos":"پوائنٹ آف سیل",
        "products":"مصنوعات",
        "reports":"رپورٹس",
        "settings":"سیٹنگز",
        "change_password":"پاس ورڈ تبدیل کریں",
        "save_product": "محفوظ کریں",
        "add_product": "نیا پروڈکٹ",
        "stock_reorder": "اسٹاک ری آرڈر",
    }
}

def t(lang: str, key: str) -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)
