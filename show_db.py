"""
show_db.py - Display AccessMap database contents
Use this to view and screenshot the database for your report
"""
import sqlite3
import os

DB_PATH = 'instance/accessmap.db'

if not os.path.exists(DB_PATH):
    print(f"❌ Database not found at: {DB_PATH}")
    print("   Run app.py at least once first.")
    exit()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=" * 80)
print("  ACCESSMAP DATABASE - CONTENT VIEWER")
print(f"  Path: {os.path.abspath(DB_PATH)}")
print(f"  Size: {os.path.getsize(DB_PATH)} bytes")
print("=" * 80)

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"\n📋 TABLES FOUND: {len(tables)}")
print("-" * 80)
for i, (table_name,) in enumerate(tables, 1):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"  {i}. {table_name:<20} ({count} rows)")

for (table_name,) in tables:
    print("\n" + "=" * 80)
    print(f"  📊 TABLE: {table_name.upper()}")
    print("=" * 80)

    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"\n  Columns ({len(columns)}):")
    for col in columns:
        print(f"    • {col}")

    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    print(f"\n  Data ({len(rows)} rows):")
    print("  " + "-" * 76)
    if not rows:
        print("  (No data yet)")
    else:
        for row in rows:
            display = tuple(
                (str(v)[:30] + '..') if isinstance(v, str) and len(v) > 30 else v
                for v in row
            )
            print(f"  {display}")

print("\n" + "=" * 80)
print("  ✅ VIEW COMPLETE")
print("=" * 80)

conn.close()