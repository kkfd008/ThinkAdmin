import sqlite3
import os

db_path = r"d:\dev\project\ThinkAdmin\database\sqlite.db"

if not os.path.exists(db_path):
    print(f"Database file NOT found: {db_path}")
    exit(1)

print(f"Database: {db_path}")
print(f"Size: {os.path.getsize(db_path)} bytes\n")

db = sqlite3.connect(db_path)
cursor = db.cursor()

# List all tables
cursor.execute("SELECT name, type FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"=== Tables ({len(tables)}) ===")
for name, t in tables:
    cursor.execute(f"PRAGMA table_info('{name}')")
    cols = cursor.fetchall()
    col_list = [f"{c[1]} {c[2]}" for c in cols]
    print(f"\n  {name} ({len(cols)} columns)")
    for c in cols:
        pk = " PK" if c[5] else ""
        nn = " NOT NULL" if c[3] else ""
        dv = f" DEFAULT {c[4]}" if c[4] is not None else ""
        print(f"    {c[1]:20s} {c[2]:10s}{pk}{nn}{dv}")

# Check for shop_ tables
shop_tables = [name for name, _ in tables if name.startswith('shop_')]
print(f"\n=== Shop tables: {len(shop_tables)} ===")
for t in shop_tables:
    print(f"  + {t}")

if not shop_tables:
    print("  (none - need to create via SQL)")

db.close()

# Also list SQL files
print("\n=== Available SQL files in database/ ===")
sql_dir = r"d:\dev\project\ThinkAdmin\database"
for f in os.listdir(sql_dir):
    if f.endswith('.sql'):
        filepath = os.path.join(sql_dir, f)
        print(f"  {f} ({os.path.getsize(filepath)} bytes)")
