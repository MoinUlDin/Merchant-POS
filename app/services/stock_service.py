# app/services/stock_service.py
from app.services.db_sqlite3 import get_connection
from datetime import datetime
from typing import Optional


class StockService:
    def __init__(self):
        self.conn = get_connection()

    def record_movement(self,
                        product_id: int,
                        qty: float,
                        reason: str,
                        reference_id: Optional[int] = None,
                        related_doc: Optional[str] = None,
                        unit: Optional[str] = None,
                        cost_total: Optional[float] = None,
                        created_by: Optional[str] = None) -> float:
        """
        Record a stock movement and update products.stock_qty atomically.

        - qty: quantity in the product's base unit (positive for incoming, negative for outgoing).
        - reason: 'purchase_receipt', 'sale', 'manual_adjust', 'return', ...
        - cost_total: money amount in rupees (float) OR paisa int. If float, multiplied by 100.
        - Returns the new stock_qty (float).
        """

        cur = self.conn.cursor()
        try:
            # fetch product to determine default unit and current stock
            cur.execute("SELECT unit, stock_qty FROM products WHERE id = ?", (product_id,))
            p = cur.fetchone()
            if p is None:
                raise ValueError(f"product id {product_id} not found")
            product_unit, current_stock = p[0], float(p[1] or 0.0)
            action_unit = unit if unit is not None else product_unit

            cost_total_paisa = None
            if cost_total is not None:
                try:
                    cost_total_paisa = int(cost_total)
                except Exception:
                    cost_total_paisa = None

            now = datetime.now().isoformat()

            # Insert movement
            cur.execute("""
                INSERT INTO stock_movements (product_id, qty, reason, reference_id, related_doc, unit, cost_total, created_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                float(qty),
                reason,
                reference_id,
                related_doc,
                action_unit,
                cost_total_paisa,
                now,
                created_by
            ))

            # update product stock_qty
            new_stock = current_stock + float(qty)
            cur.execute("UPDATE products SET stock_qty = ?, updated_at = ? WHERE id = ?", (new_stock, now, product_id))

            # insert audit log for stock change
            details = f'stock movement for product id{product_id}: reason="{reason}", qty={qty}, new_stock={new_stock}'
            cur.execute("INSERT INTO audit_logs (entity_type, action, details) VALUES (?, ?, ?)",
                        ("product", "stock_movement", details))

            self.conn.commit()
            return new_stock
        except Exception:
            self.conn.rollback()
            raise

    # convenience: receive by number of packs (supply_pack_qty * num_packs)
    def receive_packs(self, product_id: int, num_packs: int, reason: str = "purchase_receipt",
                      cost_total: Optional[float] = None, created_by: Optional[str] = None, reference_id: Optional[int] = None) -> float:
        """
        Add stock using the product.supply_pack_qty. E.g. sugar supply_pack_qty=50 (kg per bag);
        receive_packs(product_id, 5) will add 5 * 50 = 250 (base unit) to stock.
        cost_total (optional): total cost in rupees (or paisa int); it's stored on movement.cost_total column.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT supply_pack_qty FROM products WHERE id = ?", (product_id,))
        row = cur.fetchone()
        if row is None:
            raise ValueError("product not found")
        pack_size = float(row[0] or 1.0)
        added_qty = pack_size * int(num_packs)
        print(f"productId: {id}, size: {pack_size}, Added: {added_qty}")
        return self.record_movement(product_id=product_id, qty=added_qty, reason=reason,
                                    reference_id=reference_id, cost_total=cost_total, created_by=created_by)

    # convenience: consume stock for a sale (negative qty)
    def consume_for_sale(self, product_id: int, qty: float, sale_id: Optional[int] = None, created_by: Optional[str] = None) -> float:
        """
        Record negative movement for sale and update product stock.
        qty should be in base unit (e.g., 0.5 for 500g if unit is kg).
        """
        return self.record_movement(product_id=product_id, qty=-abs(float(qty)), reason="sale",
                                    reference_id=sale_id, created_by=created_by)
