import sqlite3
import unittest

from werkzeug.security import generate_password_hash

from database.db import FinanceDatabase
from webapp.app import app

class TestAppRoutes(unittest.TestCase):
    # Routes are now behind login (see webapp/auth.py). Rather than mock
    # flask-login's session internals, log in for real through /login so
    # these tests exercise the same path a browser does.
    TEST_USERNAME = "test_auth_user"
    TEST_PASSWORD = "test-password-not-for-real-use"

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self._ensure_test_user_exists()
        self.client.post('/login', data={
            'username': self.TEST_USERNAME,
            'password': self.TEST_PASSWORD,
        })

    def _ensure_test_user_exists(self):
        # get_db_connection() in app.py opens the DB file as-is and assumes
        # init_db.py already ran; on a fresh checkout/CI run that file may
        # have no tables at all. FinanceDatabase's constructor is the same
        # schema-creation path init_db.py uses, so run it first to guarantee
        # `users` (and everything else) exists before querying it directly.
        FinanceDatabase(app.config['DATABASE']).close()

        conn = sqlite3.connect(app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                'SELECT id FROM users WHERE username = ?', (self.TEST_USERNAME,)
            ).fetchone()
            if row is not None:
                return
            household = conn.execute('SELECT id FROM households LIMIT 1').fetchone()
            if household is None:
                cur = conn.execute(
                    'INSERT INTO households (name) VALUES (?)', ('Test Household',)
                )
                household_id = cur.lastrowid
            else:
                household_id = household['id']
            conn.execute(
                'INSERT INTO users (household_id, username, password_hash) VALUES (?, ?, ?)',
                (household_id, self.TEST_USERNAME, generate_password_hash(self.TEST_PASSWORD)),
            )
            conn.commit()
        finally:
            conn.close()

    def test_index_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Transactions', response.data)

    def test_dashboard_route(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)

    def test_add_route_get(self):
        response = self.client.get('/add')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add', response.data)

    def test_api_expenses_by_category(self):
        response = self.client.get('/api/expenses_by_category')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

    def test_api_monthly_cash_flow(self):
        response = self.client.get('/api/monthly_cash_flow')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

    def test_api_income_vs_expenses(self):
        response = self.client.get('/api/income_vs_expenses')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

    def test_api_donations_vs_income(self):
        response = self.client.get('/api/donations_vs_income')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)

if __name__ == '__main__':
    unittest.main()
