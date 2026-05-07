import sqlite3
import os

db_path = r"d:\dev\project\ThinkAdmin\database\sqlite.db"

if not os.path.exists(db_path):
    print(f"Error: Database file not found: {db_path}")
    exit(1)

db = sqlite3.connect(db_path)
cursor = db.cursor()

# ========== 超市管理相关表 ==========

# 1. 供应商表
cursor.execute("""
CREATE TABLE IF NOT EXISTS shop_supplier (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL DEFAULT '',
    code VARCHAR(50) DEFAULT '',
    contact VARCHAR(50) DEFAULT '',
    phone VARCHAR(20) DEFAULT '',
    address VARCHAR(255) DEFAULT '',
    category VARCHAR(50) DEFAULT '',
    status INTEGER DEFAULT 1,
    remark TEXT,
    is_deleted INTEGER DEFAULT 0,
    create_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP,
    update_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# 2. 商品表
cursor.execute("""
CREATE TABLE IF NOT EXISTS shop_product (
    id INTEGER PRIMARY KEY,
    code VARCHAR(50) DEFAULT '',
    barcode VARCHAR(100) DEFAULT '',
    name VARCHAR(100) NOT NULL DEFAULT '',
    category VARCHAR(50) DEFAULT '',
    supplier_id INTEGER DEFAULT 0,
    price DECIMAL(10,2) DEFAULT '0.00',
    cost_price DECIMAL(10,2) DEFAULT '0.00',
    unit VARCHAR(20) DEFAULT '件',
    specs VARCHAR(200) DEFAULT '',
    image VARCHAR(255) DEFAULT '',
    status INTEGER DEFAULT 1,
    is_deleted INTEGER DEFAULT 0,
    create_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP,
    update_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# 3. 库存表
cursor.execute("""
CREATE TABLE IF NOT EXISTS shop_stock (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL DEFAULT 0,
    stock INTEGER DEFAULT 0,
    min_stock INTEGER DEFAULT 10,
    warehouse VARCHAR(50) DEFAULT '',
    location VARCHAR(100) DEFAULT '',
    is_deleted INTEGER DEFAULT 0,
    create_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP,
    update_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_shop_stock_product ON shop_stock(product_id)")

# 4. 库存日志表
cursor.execute("""
CREATE TABLE IF NOT EXISTS shop_stock_log (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL DEFAULT 0,
    type INTEGER DEFAULT 1,
    quantity INTEGER NOT NULL DEFAULT 0,
    before_stock INTEGER DEFAULT 0,
    after_stock INTEGER DEFAULT 0,
    operator VARCHAR(50) DEFAULT '',
    remark VARCHAR(200) DEFAULT '',
    is_deleted INTEGER DEFAULT 0,
    create_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_sl_product ON shop_stock_log(product_id)")

# ========== 发货单相关表 ==========

# 5. 发货单表
cursor.execute("""
CREATE TABLE IF NOT EXISTS shop_delivery (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200) DEFAULT '',
    customer VARCHAR(200) DEFAULT '',
    delivery_date DATE,
    sheet_name VARCHAR(100) DEFAULT '',
    total_amount DECIMAL(12,2) DEFAULT '0.00',
    item_count INTEGER DEFAULT 0,
    total_quantity INTEGER DEFAULT 0,
    operator VARCHAR(50) DEFAULT '',
    operator_name VARCHAR(50) DEFAULT '',
    remark VARCHAR(500) DEFAULT '',
    is_deleted INTEGER DEFAULT 0,
    create_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP,
    update_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_sd_date ON shop_delivery(delivery_date)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_sd_customer ON shop_delivery(customer)")

# 6. 发货明细表
cursor.execute("""
CREATE TABLE IF NOT EXISTS shop_delivery_item (
    id INTEGER PRIMARY KEY,
    delivery_id INTEGER NOT NULL DEFAULT 0,
    row_no INTEGER DEFAULT 0,
    barcode VARCHAR(100) DEFAULT '',
    name VARCHAR(200) NOT NULL DEFAULT '',
    box_spec DECIMAL(10,2) DEFAULT '0.00',
    box_count DECIMAL(10,4) DEFAULT '0.0000',
    quantity INTEGER NOT NULL DEFAULT 0,
    unit VARCHAR(20) DEFAULT '个',
    cost_price DECIMAL(10,2) DEFAULT '0.00',
    total_amount DECIMAL(10,2) DEFAULT '0.00',
    retail_price DECIMAL(10,2) DEFAULT '0.00',
    product_id INTEGER DEFAULT 0,
    is_deleted INTEGER DEFAULT 0,
    create_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_sdi_delivery ON shop_delivery_item(delivery_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_sdi_barcode ON shop_delivery_item(barcode)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_sdi_product ON shop_delivery_item(product_id)")

db.commit()

# Verify
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'shop_%' ORDER BY name")
shop_tables = [r[0] for r in cursor.fetchall()]
print("Created/Verified shop_ tables:")
for t in shop_tables:
    cursor.execute(f"PRAGMA table_info('{t}')")
    cols = cursor.fetchall()
    print(f"  + {t} ({len(cols)} columns)")

db.close()
print("\nDone! All tables created successfully.")
