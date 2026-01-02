# app/services/db_sqlite3.py
import os, sqlite3
from pathlib import Path

def get_default_db_path():
    appdata = os.getenv("APPDATA") or str(Path.home())
    folder = Path(appdata) / "MyShopApp"
    folder.mkdir(parents=True, exist_ok=True)
    return str(folder / "shop.db")

_conn = None

def get_connection(db_path: str | None = None):
    global _conn
    if _conn:
        return _conn
    if db_path is None:
        db_path = get_default_db_path()
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    _conn = conn
    return conn
