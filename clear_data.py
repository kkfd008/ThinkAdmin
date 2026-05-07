import sqlite3

db = sqlite3.connect(r'd:\dev\project\ThinkAdmin\database\sqlite.db')
cur = db.cursor()

tables = [
    ('shop_delivery_item', u'\u660e\u7ec6'),
    ('shop_delivery', u'\u5165\u5e93\u5355'),
    ('shop_stock_log', u'\u5e93\u5b58\u65e5\u5fd7'),
    ('shop_stock', u'\u5e93\u5b58'),
    ('shop_product', u'\u5546\u54c1'),
]

for tbl, label in tables:
    cur.execute('DELETE FROM %s' % tbl)
    print('  %s (%s): %d rows' % (tbl, label, cur.rowcount))

db.commit()
db.close()
print('\nDone.')
