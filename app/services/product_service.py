# app/services/product_service.py
from app.services.db_sqlite3 import get_connection
from datetime import datetime
from typing import Optional, List, Dict, Any


def _to_paisa(value) -> int:
    """
    Convert a rupee float/string/int to paisa integer.
    If value already looks like an int (and user intended paisa) caller should pass price_paisa explicitly.
    """
    if value is None:
        return 0
    # if it's an int, assume it's paisa already only if caller passed with price_paisa kwarg.
    # But to be safe: treat numeric non-float as rupee as well (e.g., 180 -> 18000 paisa)
    try:
        v = float(value)
    except Exception:
        return 0
    return int(round(v * 100))


class ProductService:
    def __init__(self):
        self.conn = get_connection()

    # -----------------------
    # Read ops
    # -----------------------
    def all_products(self) -> List[tuple]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id, short_code, ur_name, en_name, company, barcode,
                   base_price, sell_price, stock_qty, reorder_threshold,
                   category_id, unit, custom_packing, packing_size, supply_pack_qty,
                   created_at, updated_at
            FROM products
            ORDER BY ur_name
        """)
        return cur.fetchall()

    def get(self, product_id: int) -> Optional[tuple]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id, short_code, ur_name, en_name, company, barcode,
                   base_price, sell_price, stock_qty, reorder_threshold,
                   category_id, unit, custom_packing, packing_size, supply_pack_qty,
                   created_at, updated_at
            FROM products WHERE id = ?
        """, (product_id,))
        return cur.fetchone()

    def find_by_barcode(self, barcode: str) -> Optional[tuple]:
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM products WHERE barcode = ?", (barcode,))
        return cur.fetchone()

    def search(self, term: str, limit: int = 50) -> List[tuple]:
        cur = self.conn.cursor()
        q = f"%{term}%"
        cur.execute("""
            SELECT id, short_code, ur_name, en_name, company, barcode, sell_price, stock_qty
            FROM products
            WHERE ur_name LIKE ? OR en_name LIKE ? OR barcode LIKE ? OR short_code LIKE ?
            ORDER BY ur_name LIMIT ?
        """, (q, q, q, q, limit))
        return cur.fetchall()

    # -----------------------
    # Create / Update / Delete
    # -----------------------
    def create(self, data: Dict[str, Any]) -> int:
        """
        Create product. Accepts:
          - base_price (in rupees) or base_price_paisa
          - sell_price (in rupees) or sell_price_paisa
        Returns inserted product id.
        """
        cur = self.conn.cursor()

        # price conversion: prefer explicit paisa keys if provided
        base_price_paisa = data.get("base_price_paisa")
        if base_price_paisa is None:
            base_price_paisa = _to_paisa(data.get("base_price"))

        sell_price_paisa = data.get("sell_price_paisa")
        if sell_price_paisa is None:
            sell_price_paisa = _to_paisa(data.get("sell_price"))

        now = datetime.now().isoformat()
        try:
            cur.execute("""
                INSERT INTO products
                (short_code, ur_name, en_name, company, barcode,
                 base_price, sell_price, stock_qty, reorder_threshold,
                 category_id, unit, custom_packing, packing_size, supply_pack_qty,
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("short_code"),
                data.get("ur_name"),
                data.get("en_name"),
                data.get("company"),
                data.get("barcode"),
                int(base_price_paisa),
                int(sell_price_paisa),
                float(data.get("stock_qty", 0)),
                float(data.get("reorder_threshold", 0)),
                data.get("category_id"),
                data.get("unit", "kg"),
                1 if data.get("custom_packing") else 0,
                data.get("packing_size"),
                float(data.get("supply_pack_qty", 1.0)),
                now,
                now
            ))
            product_id = cur.lastrowid

            # audit
            details = f'product created with id{product_id} name="{data.get("ur_name") or data.get("en_name")}"'
            cur.execute("INSERT INTO audit_logs (entity_type, action, details) VALUES (?, ?, ?)",
                        ("product", "create", details))

            self.conn.commit()
            return product_id
        except Exception:
            self.conn.rollback()
            raise

    def update(self, product_id: int, data: Dict[str, Any]) -> bool:
        """
        Update product and write audit log entries for changed fields.
        Data may contain rupee prices or explicit *_paisa fields.
        """
        cur = self.conn.cursor()
        # snapshot
        cur.execute("""
            SELECT id, short_code, ur_name, en_name, company, barcode,
                   base_price, sell_price, stock_qty, reorder_threshold,
                   category_id, unit, custom_packing, packing_size, supply_pack_qty
            FROM products WHERE id = ?
        """, (product_id,))
        old = cur.fetchone()
        if old is None:
            raise ValueError(f"product id {product_id} not found")

        old_map = {
            "short_code": old[1],
            "ur_name": old[2],
            "en_name": old[3],
            "company": old[4],
            "barcode": old[5],
            "base_price": old[6],
            "sell_price": old[7],
            "stock_qty": old[8],
            "reorder_threshold": old[9],
            "category_id": old[10],
            "unit": old[11],
            "custom_packing": old[12],
            "packing_size": old[13],
            "supply_pack_qty": old[14],
        }

        # prepare prices
        base_price_paisa = data.get("base_price_paisa")
        if base_price_paisa is None and "base_price" in data:
            base_price_paisa = _to_paisa(data.get("base_price"))
        elif base_price_paisa is None:
            base_price_paisa = old_map["base_price"]

        sell_price_paisa = data.get("sell_price_paisa")
        if sell_price_paisa is None and "sell_price" in data:
            sell_price_paisa = _to_paisa(data.get("sell_price"))
        elif sell_price_paisa is None:
            sell_price_paisa = old_map["sell_price"]

        now = datetime.now().isoformat()
        try:
            cur.execute("""
                UPDATE products SET
                  short_code = ?, ur_name = ?, en_name = ?, company = ?, barcode = ?,
                  base_price = ?, sell_price = ?, stock_qty = ?, reorder_threshold = ?,
                  category_id = ?, unit = ?, custom_packing = ?, packing_size = ?, supply_pack_qty = ?,
                  updated_at = ?
                WHERE id = ?
            """, (
                data.get("short_code", old_map["short_code"]),
                data.get("ur_name", old_map["ur_name"]),
                data.get("en_name", old_map["en_name"]),
                data.get("company", old_map["company"]),
                data.get("barcode", old_map["barcode"]),
                int(base_price_paisa),
                int(sell_price_paisa),
                float(data.get("stock_qty", old_map["stock_qty"])),
                float(data.get("reorder_threshold", old_map["reorder_threshold"])),
                data.get("category_id", old_map["category_id"]),
                data.get("unit", old_map["unit"]),
                1 if data.get("custom_packing", old_map["custom_packing"]) else 0,
                data.get("packing_size", old_map["packing_size"]),
                float(data.get("supply_pack_qty", old_map["supply_pack_qty"])),
                now,
                product_id
            ))

            # generate audit messages (single combined or per-field)
            changed = []
            check_fields = ["short_code","ur_name","en_name","company","barcode",
                            "base_price","sell_price","stock_qty","reorder_threshold",
                            "category_id","unit","custom_packing","packing_size","supply_pack_qty"]
            for f in check_fields:
                new_val = None
                if f in ("base_price","sell_price"):
                    new_val = int(base_price_paisa) if f == "base_price" else int(sell_price_paisa)
                else:
                    new_val = data.get(f, old_map.get(f))
                old_val = old_map.get(f)
                # compare as strings for simplicity
                if str(old_val) != str(new_val):
                    details = f'product {f} with id{product_id} changed from "{old_val}" to "{new_val}"'
                    changed.append(details)
                    cur.execute("INSERT INTO audit_logs (entity_type, action, details) VALUES (?, ?, ?)",
                                ("product", "update", details))

            self.conn.commit()
            return True
        except Exception:
            self.conn.rollback()
            raise

    def delete(self, product_id: int) -> bool:
        cur = self.conn.cursor()
        try:
            # attempt delete; will fail if FK restrict exists (sale_items)
            cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
            if cur.rowcount == 0:
                self.conn.rollback()
                return False
            details = f'product deleted with id{product_id}'
            cur.execute("INSERT INTO audit_logs (entity_type, action, details) VALUES (?, ?, ?)",
                        ("product", "delete", details))
            self.conn.commit()
            return True
        except Exception:
            self.conn.rollback()
            raise

    # -----------------------
    # Utility
    # -----------------------
    def adjust_stock(self, product_id: int, delta_qty: float, reason: str = "manual_adjust", created_by: Optional[str] = None) -> float:
        """
        Adjust product.stock_qty by delta_qty (positive or negative).
        Also inserts a stock_movements row. Returns new stock_qty.
        """
        from app.services.stock_service import StockService
        ss = StockService()
        return ss.record_movement(product_id=product_id, qty=delta_qty, reason=reason, created_by=created_by)
