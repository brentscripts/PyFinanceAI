import sqlite3
import unittest

from werkzeug.security import generate_password_hash

from database.db import FinanceDatabase
from webapp.app import app


class TestAuth(unittest.TestCase):
    TEST_USERNAME = "test_auth_flow_user"
    TEST_PASSWORD = "test-password-not-for-real-use"

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self._ensure_test_user_exists()

    def _ensure_test_user_exists(self):
        # See the matching comment in test_app.py: this guarantees the
        # schema exists before querying `users` directly, instead of
        # assuming init_db.py already ran against this DB file.
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

    def test_index_redirects_to_login_when_anonymous(self):
        response = self.client.get('/', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

    def test_api_route_returns_401_json_when_anonymous(self):
        response = self.client.get('/api/expenses_by_category')
        self.assertEqual(response.status_code, 401)
        self.assertTrue(response.is_json)

    def test_login_with_wrong_password_shows_error(self):
        response = self.client.post('/login', data={
            'username': self.TEST_USERNAME,
            'password': 'definitely-not-it',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password', response.data)

    def test_login_then_access_protected_route(self):
        login_response = self.client.post('/login', data={
            'username': self.TEST_USERNAME,
            'password': self.TEST_PASSWORD,
        }, follow_redirects=True)
        self.assertEqual(login_response.status_code, 200)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Transactions', response.data)

    def test_logout_revokes_access(self):
        self.client.post('/login', data={
            'username': self.TEST_USERNAME,
            'password': self.TEST_PASSWORD,
        })
        self.client.post('/logout')

        response = self.client.get('/', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])


if __name__ == '__main__':
    unittest.main()
