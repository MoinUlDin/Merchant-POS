-- schema.sql
-- Basic schema for Kiryana Store POS

BEGIN TRANSACTION;

-- users table (single-admin)
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  salt TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
-- categories table (if not already present)
CREATE TABLE IF NOT EXISTS categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- products table (example, should match your design)
CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  short_code TEXT UNIQUE,
  ur_name TEXT NOT NULL,
  en_name TEXT,
  company TEXT,
  barcode TEXT UNIQUE,
  base_price INTEGER DEFAULT 0,     -- cost per base-unit in paisa (integer)
  sell_price INTEGER DEFAULT 0,     -- sell price per base-unit in paisa
  stock_qty REAL DEFAULT 0,               -- quantity in base unit (e.g., kg)
  reorder_threshold REAL DEFAULT 0,
  category_id INTEGER,
  unit TEXT DEFAULT 'kg',                 -- 'kg','gram','ltr','ml','pcs'
  custom_packing INTEGER DEFAULT 0,
  packing_size REAL,
  supply_pack_qty REAL DEFAULT 1.0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME,
  FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS product_short_idx ON products(short_code);
CREATE INDEX IF NOT EXISTS product_barcode_idx ON products(barcode);
CREATE INDEX IF NOT EXISTS product_company_idx ON products(company);

-- sales master record: one row per sale/receipt
CREATE TABLE IF NOT EXISTS sales (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_by TEXT,                 -- username or user id (optional)
  total_before_discounts INTEGER NOT NULL DEFAULT 0,  -- sum of line totals
  discount INTEGER NOT NULL DEFAULT 0,                -- total discount applied (sale-level)
  tax INTEGER NOT NULL DEFAULT 0,                     -- tax for the sale if any
  charged_total INTEGER NOT NULL DEFAULT 0,           -- final amount received (total_before - discount + tax)
  payment_method TEXT,
  note TEXT
);

-- sale items: one row per product line on a sale (historical snapshot)
CREATE TABLE IF NOT EXISTS sale_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sale_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  qty REAL NOT NULL,               -- qty in product base unit (e.g., kg)
  input_unit TEXT NOT NULL,        -- the unit cashier used (e.g., 'gram' or 'kg')
  price_per_unit INTEGER NOT NULL, -- price per base unit used for this sale (may be overridden)
  base_price_per_unit INTEGER NOT NULL, -- product cost per base unit at time of sale
  line_total INTEGER NOT NULL,     -- qty * price_per_unit (rounded)
  line_cost_total INTEGER NOT NULL,-- qty * base_price_per_unit
  line_discount INTEGER NOT NULL DEFAULT 0, -- discount applied to this line (if any)
  line_charged INTEGER NOT NULL,   -- final amount collected for this line (line_total - line_discount)
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);

-- stock / inventory receipts and general movements (append-only)
CREATE TABLE IF NOT EXISTS stock_movements (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL,
  qty REAL NOT NULL,          -- positive for incoming, negative for outgoing (in base unit)
  reason TEXT NOT NULL,       -- 'sale', 'purchase_receipt', 'manual_adjust', 'return', 'inventory_correction'
  reference_id INTEGER,       -- optional: sale_id or purchase_id
  related_doc TEXT,           -- optional extra text with supplier/order ref
  unit TEXT,                  -- unit used in this movement (mirror product.unit)
  cost_total INTEGER,         -- cost for incoming movements (purchase cost)
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  created_by TEXT,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);



CREATE TABLE IF NOT EXISTS audit_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entity_type TEXT NOT NULL,   -- e.g. 'product', 'sale', 'user'
  action TEXT NOT NULL,        -- e.g. 'update', 'create', 'delete', 'price_change'
  details TEXT NOT NULL,       -- human readable message describing the change
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- helpful index for time-based queries and filtering by entity
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_type ON audit_logs(entity_type);


COMMIT;
