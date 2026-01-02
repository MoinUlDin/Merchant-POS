# app/services/product_service.py
from app.services.db_sqlite3 import get_connection
from datetime import datetime

class ProductService:
    def __init__(self):
        self.conn = get_connection()

    def all_products(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id, ur_name, en_name, company,
                   base_price, sell_price,
                   stock_qty, reorder_threshold
            FROM products
            ORDER BY ur_name
        """)
        return cur.fetchall()

    def get(self, product_id):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        return cur.fetchone()

    def create(self, data):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO products
            (ur_name, en_name, company, barcode,
             base_price, sell_price, stock_qty, reorder_threshold)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["ur_name"],
            data.get("en_name"),
            data.get("company"),
            data.get("barcode"),
            data["base_price"],
            data["sell_price"],
            data["stock_qty"],
            data["reorder_threshold"],
        ))
        self.conn.commit()
        return True

    def update(self, product_id, data):
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE products SET
              ur_name = ?, en_name = ?, company = ?, barcode = ?,
              base_price = ?, sell_price = ?, stock_qty = ?, reorder_threshold = ?,
              updated_at = ?
            WHERE id = ?
        """, (
            data["ur_name"],
            data.get("en_name"),
            data.get("company"),
            data.get("barcode"),
            data["base_price"],
            data["sell_price"],
            data["stock_qty"],
            data["reorder_threshold"],
            datetime.now().isoformat(),
            product_id
        ))
        self.conn.commit()
