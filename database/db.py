import sqlite3
from typing import List, Tuple

class FinanceDatabase:
    def __init__(self, db_path="finance.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables_if_not_exists()

    def _create_tables_if_not_exists(self):
        """Create the transactions table if it doesn't already exist."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            post_date TEXT,
            description TEXT,
            original_description TEXT,
            category TEXT,
            amount REAL,
            type TEXT,
            account TEXT,
            source TEXT,
            tags TEXT,
            memo TEXT
        )
        """)
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
