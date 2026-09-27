"""
One-time helper for the Data Model Rework migration.

Populates the `categories` table from whatever category text already
exists in `transactions` (from bank/Chase CSV imports), then links each
transaction's new `category_id` column to the matching row.

The old free-text `transactions.category` column is left untouched — the
UI, filters, and charts still read from it until the Categorization Engine
phase switches them over to `category_id`.

Safe to re-run: category names are inserted with INSERT OR IGNORE, and the
UPDATE only touches rows where category_id is still NULL.
"""
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()


def backfill():
    db_path = os.environ.get("DATABASE", "finance.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT category FROM transactions
        WHERE category IS NOT NULL AND TRIM(category) <> ''
    """)
    names = [row[0] for row in cursor.fetchall()]

    cursor.executemany(
        "INSERT OR IGNORE INTO categories (name) VALUES (?)",
        [(name,) for name in names],
    )

    cursor.execute("""
        UPDATE transactions
        SET category_id = (
            SELECT id FROM categories WHERE categories.name = transactions.category
        )
        WHERE category_id IS NULL
          AND category IS NOT NULL
          AND TRIM(category) <> ''
    """)
    linked = cursor.rowcount

    conn.commit()
    conn.close()
    print(f"✅ Seeded {len(names)} categories and linked {linked} transactions.")


if __name__ == "__main__":
    backfill()
