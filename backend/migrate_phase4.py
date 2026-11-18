"""
Migration script for Phase 4: Orders & Order Items enhancements.
Safe to re-run multiple times.
Run from backend/ with venv active:
    python migrate_phase4.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import text
from app.db.session import engine

COLUMNS = [
    # Table, Column, SQL
    ("orders", "customer_name", "ALTER TABLE orders ADD COLUMN customer_name VARCHAR(150)"),
    ("orders", "customer_email", "ALTER TABLE orders ADD COLUMN customer_email VARCHAR(255)"),
    ("orders", "customer_phone", "ALTER TABLE orders ADD COLUMN customer_phone VARCHAR(25)"),
    ("orders", "subtotal", "ALTER TABLE orders ADD COLUMN subtotal NUMERIC(10, 2) DEFAULT 0.00"),
    ("orders", "delivery_fee", "ALTER TABLE orders ADD COLUMN delivery_fee NUMERIC(10, 2) DEFAULT 0.00"),
    ("orders", "payment_method", "ALTER TABLE orders ADD COLUMN payment_method VARCHAR(30) DEFAULT 'cash_on_delivery'"),
    ("order_items", "product_name_snapshot", "ALTER TABLE order_items ADD COLUMN product_name_snapshot VARCHAR(150)"),
    ("order_items", "line_total", "ALTER TABLE order_items ADD COLUMN line_total NUMERIC(10, 2) DEFAULT 0.00"),
]


def column_exists(conn, table: str, column: str) -> bool:
    row = conn.execute(text("""
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_name = :tbl AND column_name = :col
    """), {"tbl": table, "col": column}).scalar()
    return row > 0


def run():
    with engine.begin() as conn:
        for table, column, sql in COLUMNS:
            if column_exists(conn, table, column):
                print(f"  skip  {table}.{column} (already exists)")
            else:
                try:
                    conn.execute(text(sql))
                    print(f"  done  {table}.{column}")
                except Exception as e:
                    print(f"  WARN  {table}.{column}: {e}")

    print("\n✅  Phase 4 Migration complete!\n")


if __name__ == "__main__":
    run()
