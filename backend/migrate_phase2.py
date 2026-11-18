"""
Migration script — adds new columns to existing tables for Phase 2.
Safe to run multiple times (checks if column exists before adding).

Run from backend/ with venv active:
    python migrate_phase2.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import text
from app.db.session import engine


MIGRATIONS = [
    # ── categories ──────────────────────────────────────────────────────────
    ("categories", "slug",
     "ALTER TABLE categories ADD COLUMN slug VARCHAR(120) UNIQUE"),
    ("categories", "is_active",
     "ALTER TABLE categories ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE"),

    # ── products ─────────────────────────────────────────────────────────────
    # Rename old 'price' to 'selling_price' if it exists
    ("products", "selling_price",
     "ALTER TABLE products RENAME COLUMN price TO selling_price"),
    # Add new product columns
    ("products", "slug",
     "ALTER TABLE products ADD COLUMN slug VARCHAR(180) UNIQUE"),
    ("products", "cost_price",
     "ALTER TABLE products ADD COLUMN cost_price NUMERIC(10,2)"),
    ("products", "unit",
     "ALTER TABLE products ADD COLUMN unit VARCHAR(30)"),
    ("products", "quality_notes",
     "ALTER TABLE products ADD COLUMN quality_notes TEXT"),
    ("products", "expiry_info",
     "ALTER TABLE products ADD COLUMN expiry_info VARCHAR(200)"),
    ("products", "created_at",
     "ALTER TABLE products ADD COLUMN created_at TIMESTAMPTZ DEFAULT NOW()"),
    ("products", "updated_at",
     "ALTER TABLE products ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW()"),

    # ── reviews ──────────────────────────────────────────────────────────────
    # Rename 'comment' to 'body' if column exists as 'comment'
    ("reviews", "body",
     "ALTER TABLE reviews RENAME COLUMN comment TO body"),
]


def column_exists(conn, table: str, column: str) -> bool:
    row = conn.execute(text("""
        SELECT COUNT(*) FROM information_schema.columns
        WHERE table_name = :tbl AND column_name = :col
    """), {"tbl": table, "col": column}).scalar()
    return row > 0


def run():
    with engine.begin() as conn:
        for table, column, sql in MIGRATIONS:
            if column_exists(conn, table, column):
                print(f"  skip  {table}.{column}  (already exists)")
            else:
                # For RENAME, we need to check the OLD column name
                if "RENAME COLUMN" in sql:
                    old_col = sql.split("RENAME COLUMN")[1].split("TO")[0].strip()
                    if not column_exists(conn, table, old_col):
                        print(f"  skip  {table} RENAME {old_col}→{column} (old column missing, nothing to rename)")
                        continue
                try:
                    conn.execute(text(sql))
                    print(f"  done  {table}.{column}")
                except Exception as e:
                    print(f"  WARN  {table}.{column}: {e}")

        # Back-fill slug for products that have a name but no slug yet
        print("\n  Back-filling product slugs from SKU …")
        conn.execute(text("""
            UPDATE products
            SET slug = LOWER(REPLACE(REPLACE(sku, '_', '-'), ' ', '-'))
            WHERE slug IS NULL
        """))

        # Back-fill slug for categories that have a name but no slug yet
        print("  Back-filling category slugs from name …")
        conn.execute(text("""
            UPDATE categories
            SET slug = LOWER(REPLACE(REPLACE(name, ' ', '-'), '&', 'and'))
            WHERE slug IS NULL
        """))

        # Make slug NOT NULL after back-fill
        try:
            conn.execute(text(
                "ALTER TABLE categories ALTER COLUMN slug SET NOT NULL"
            ))
            conn.execute(text(
                "ALTER TABLE products ALTER COLUMN slug SET NOT NULL"
            ))
            print("  done  slugs set NOT NULL")
        except Exception as e:
            print(f"  WARN  set NOT NULL: {e}")

    print("\n✅  Migration complete!\n")


if __name__ == "__main__":
    run()
