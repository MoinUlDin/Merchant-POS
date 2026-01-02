# init_db.py
import sqlite3, os, sys
from pathlib import Path

ROOT = Path(__file__).parent
SCHEMA = ROOT / "schema.sql"

def get_db_path():
    appdata = os.getenv("APPDATA") or str(Path.home())
    folder = Path(appdata) / "MyShopApp"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "shop.db"

def init_db(db_path=None):
    if db_path is None:
        db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    with open(SCHEMA, "r", encoding="utf-8") as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()
    conn.close()
    print("Initialized DB at:", db_path)

if __name__ == "__main__":
    init_db()
