import sqlite3
from typing import List, Tuple

class FinanceDatabase:
    def __init__(self, db_path="finance.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

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
