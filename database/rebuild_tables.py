import sqlite3

db = sqlite3.connect(r'd:\dev\project\ThinkAdmin\database\sqlite.db')
cur = db.cursor()

# 删除旧的6张表
for tbl in ['shop_delivery_item','shop_delivery','shop_stock_log','shop_stock','shop_product','shop_supplier']:
    cur.execute('DROP TABLE IF EXISTS %s' % tbl)

# 1. 供应商管理
cur.execute("""CREATE TABLE shop_supplier (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(12) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL DEFAULT '',
    phone VARCHAR(20) DEFAULT '',
    is_deleted INTEGER DEFAULT 0,
    create_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP
)""")

# 2. 商品管理
cur.execute("""CREATE TABLE shop_product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode VARCHAR(100) NOT NULL DEFAULT '',
    name VARCHAR(200) NOT NULL DEFAULT '',
    box_spec DECIMAL(10,2) DEFAULT 0,
    cost_price DECIMAL(10,2) DEFAULT 0,
    price DECIMAL(10,2) DEFAULT 0,
    is_deleted INTEGER DEFAULT 0,
    create_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP,
    update_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP
)""")

# 3. 库存
cur.execute("""CREATE TABLE shop_stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    stock INTEGER DEFAULT 0,
    is_deleted INTEGER DEFAULT 0,
    create_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP,
    update_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP
)""")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_shop_stock_product ON shop_stock(product_id)")

# 4. 库存变化记录
cur.execute("""CREATE TABLE shop_stock_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode VARCHAR(100) DEFAULT '',
    name VARCHAR(200) DEFAULT '',
    type INTEGER DEFAULT 1,
    quantity INTEGER NOT NULL DEFAULT 0,
    is_deleted INTEGER DEFAULT 0,
    create_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP
)""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_ssl_barcode ON shop_stock_log(barcode)")

# 5. 库单管理
cur.execute("""CREATE TABLE shop_delivery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER DEFAULT 0,
    supplier_name VARCHAR(100) DEFAULT '',
    delivery_date DATE,
    order_type VARCHAR(20) DEFAULT '入库',
    item_count INTEGER DEFAULT 0,
    total_quantity INTEGER DEFAULT 0,
    total_amount DECIMAL(12,2) DEFAULT 0,
    remark VARCHAR(500) DEFAULT '',
    is_deleted INTEGER DEFAULT 0,
    create_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP,
    update_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP
)""")

# 6. 入库单商品明细
cur.execute("""CREATE TABLE shop_delivery_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    delivery_id INTEGER NOT NULL DEFAULT 0,
    barcode VARCHAR(100) DEFAULT '',
    name VARCHAR(200) NOT NULL DEFAULT '',
    box_spec DECIMAL(10,2) DEFAULT 0,
    box_count DECIMAL(10,4) DEFAULT 0,
    quantity INTEGER NOT NULL DEFAULT 0,
    unit VARCHAR(20) DEFAULT '个',
    cost_price DECIMAL(10,2) DEFAULT 0,
    price DECIMAL(10,2) DEFAULT 0,
    is_deleted INTEGER DEFAULT 0,
    create_at TIMESTAMP_TEXT DEFAULT CURRENT_TIMESTAMP
)""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_sdi_delivery ON shop_delivery_item(delivery_id)")

db.commit()

# 验证
for tbl in ['shop_supplier','shop_product','shop_stock','shop_stock_log','shop_delivery','shop_delivery_item']:
    cur.execute("PRAGMA table_info('%s')" % tbl)
    cols = ['%s %s' % (r[1], r[2]) for r in cur.fetchall()]
    print('  ' + tbl + ': ' + ', '.join(cols))

db.close()
print('\nDone. All 6 tables rebuilt.')
