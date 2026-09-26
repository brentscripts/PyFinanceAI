import unittest
import sqlite3
import os
from database.db import FinanceDatabase

class TestFinanceDatabase(unittest.TestCase):
    def setUp(self):
        # Use an in-memory SQLite database for testing.
        # FinanceDatabase's constructor already creates the transactions
        # table via _create_tables_if_not_exists(), so no need to redo it here.
        self.db = FinanceDatabase(':memory:')

    def tearDown(self):
        self.db.close()

    def test_insert_transactions(self):
        transactions = [
            ('2023-01-01', None, 'Groceries', None, 'Food', -100.0, 'Debit', 'Checking', 'bank', None, None),
            ('2023-01-02', None, 'Salary', None, 'Income', 200.0, 'Credit', 'Checking', 'bank', None, None)
        ]
        self.db.insert_transactions(transactions)
        self.db.cursor.execute('SELECT * FROM transactions')
        rows = self.db.cursor.fetchall()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][3], 'Groceries')
        self.assertEqual(rows[1][3], 'Salary')
        self.assertEqual(rows[0][6], -100.0)
        self.assertEqual(rows[1][6], 200.0)

if __name__ == '__main__':
    unittest.main()
