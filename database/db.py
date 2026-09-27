import os
import sqlite3
from typing import List, Tuple

# schema.sql lives at the project root; this file lives in database/, so walk
# up one level. Resolved from this file's location (not cwd) so it works the
# same whether FinanceDatabase is instantiated from webapp/app.py, a script,
# or a test — schema.sql is the single source of truth for the table shape.
SCHEMA_PATH = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "schema.sql")
)

class FinanceDatabase:
    def __init__(self, db_path="finance.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables_if_not_exists()

    # Columns added to `transactions` after it first shipped. CREATE TABLE
    # IF NOT EXISTS in schema.sql only creates tables that don't exist yet —
    # it can't add a column to a transactions table that's already on disk
    # from before the column existed. Extend this dict when a future phase
    # adds another column to an existing table.
    _NEW_TRANSACTION_COLUMNS = {
        "account_id": "INTEGER REFERENCES accounts(id)",
        "category_id": "INTEGER REFERENCES categories(id)",
    }

    def _create_tables_if_not_exists(self):
        """Create tables from schema.sql if they don't already exist, then
        backfill any columns added to an existing table since."""
        with open(SCHEMA_PATH, "r") as f:
            schema = f.read()
        self.cursor.executescript(schema)
        self.conn.commit()
        self._add_missing_columns()

    def _add_missing_columns(self):
        existing = {row[1] for row in self.cursor.execute("PRAGMA table_info(transactions)")}
        for column, ddl in self._NEW_TRANSACTION_COLUMNS.items():
            if column not in existing:
                self.cursor.execute(f"ALTER TABLE transactions ADD COLUMN {column} {ddl}")
        self.conn.commit()
        
    def insert_transactions(self, transactions):
        sql = """
        INSERT INTO transactions (
            date, post_date, description, original_description, category,
            amount, type, account, source, tags, memo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.executemany(sql, transactions)
        self.conn.commit()

    def close(self):
        self.conn.close()
