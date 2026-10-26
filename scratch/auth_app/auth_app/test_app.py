import unittest
import os
import sqlite3
from app import app, DATABASE, init_db

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        # Ensure fresh test DB
        with app.app_context():
            init_db()

    def tearDown(self):
        # Cleanup test DB if needed
        pass

    def test_database_initialization(self):
        """Verify database and users table are created."""
        self.assertTrue(os.path.exists(DATABASE))
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        table = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(table)
        self.assertEqual(table[0], 'users')

    def test_register_and_login_flow(self):
        """Test user registration, duplicate prevention, password hashing, and login."""
        # 1. Register a new user
        response = self.client.post('/register', data={
            'full_name': 'Jane Doe',
            'email': 'jane@example.com',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registration successful', response.data)

        # 2. Check password is stored hashed in database
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = 'jane@example.com'")
        user = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(user)
        self.assertEqual(user['full_name'], 'Jane Doe')
        self.assertNotEqual(user['password_hash'], 'SecurePassword123!')
        self.assertTrue(user['password_hash'].startswith('pbkdf2:sha256'))

        # 3. Test duplicate email registration failure
        response_dup = self.client.post('/register', data={
            'full_name': 'Jane Clone',
            'email': 'jane@example.com',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!'
        }, follow_redirects=True)
        self.assertIn(b'already exists', response_dup.data)

        # 4. Test login with wrong password
        response_wrong = self.client.post('/login', data={
            'email': 'jane@example.com',
            'password': 'WrongPassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', response_wrong.data)

        # 5. Test login with correct password
        response_correct = self.client.post('/login', data={
            'email': 'jane@example.com',
            'password': 'SecurePassword123!'
        }, follow_redirects=True)
        self.assertEqual(response_correct.status_code, 200)
        self.assertIn(b'Welcome back, Jane Doe!', response_correct.data)

        # 6. Verify Dashboard access while logged in
        dash_response = self.client.get('/dashboard')
        self.assertEqual(dash_response.status_code, 200)
        self.assertIn(b'jane@example.com', dash_response.data)

        # 7. Test Logout
        logout_response = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'logged out successfully', logout_response.data)

        # 8. Verify Dashboard is protected after logout
        protected_response = self.client.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Please log in', protected_response.data)

if __name__ == '__main__':
    unittest.main()
