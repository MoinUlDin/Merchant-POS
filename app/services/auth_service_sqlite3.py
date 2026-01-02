# app/services/auth_service_sqlite3.py
import os, hashlib, binascii
from app.services.db_sqlite3 import get_connection

def _hash_password(password: str, salt: bytes) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode('utf-8'), salt, 100_000)
    return binascii.hexlify(dk).decode('ascii')

class AuthServiceSQLite3:
    def __init__(self):
        self.conn = get_connection()

    def has_user(self) -> bool:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(1) from users;")
        row = cur.fetchone()
        return (row[0] if row else 0) > 0

    def ensure_default_user(self, username: str = "Admin", default_password: str = "admin"):
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?;", (username,))
        if cur.fetchone():
            return
        salt = os.urandom(16)
        hashed = _hash_password(default_password, salt)
        cur.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?);",
                    (username, hashed, binascii.hexlify(salt).decode('ascii')))
        self.conn.commit()

    def verify_password(self, username: str, password: str) -> bool:
        cur = self.conn.cursor()
        cur.execute("SELECT password_hash, salt FROM users WHERE username = ?;", (username,))
        row = cur.fetchone()
        if not row:
            return False
        stored_hash = row["password_hash"]
        salt = binascii.unhexlify(row["salt"].encode('ascii'))
        return _hash_password(password, salt) == stored_hash

    def set_password(self, username: str, new_password: str):
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?;", (username,))
        salt = os.urandom(16)
        hashed = _hash_password(new_password, salt)
        salt_hex = binascii.hexlify(salt).decode('ascii')
        if cur.fetchone():
            cur.execute("UPDATE users SET password_hash = ?, salt = ? WHERE username = ?;",
                        (hashed, salt_hex, username))
        else:
            cur.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?);",
                        (username, hashed, salt_hex))
        self.conn.commit()
