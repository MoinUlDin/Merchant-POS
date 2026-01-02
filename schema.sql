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

-- products (Urdu + English names, en_name optional)
CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ur_name TEXT NOT NULL,
  en_name TEXT,
  company TEXT,
  barcode TEXT UNIQUE,
  base_price REAL DEFAULT 0.0,
  sell_price REAL DEFAULT 0.0,
  stock_qty INTEGER DEFAULT 0,
  reorder_threshold INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME
);

-- sales and sale_items (skeleton, for later)
CREATE TABLE IF NOT EXISTS sales (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  total REAL,
  discount REAL,
  payment_method TEXT
);

CREATE TABLE IF NOT EXISTS sale_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sale_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  qty INTEGER NOT NULL,
  price_charged REAL NOT NULL,
  base_price_at_sale REAL NOT NULL,
  FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);

COMMIT;
