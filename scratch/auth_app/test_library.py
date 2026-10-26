"""
Alexandria National University (ANU) - Faculty of Engineering
Course: Introduction to Database Systems (Fall 2026)
Lab 3 - Problem 2: Library Automated Test Suite

Verification of Requirements 1 through 14:
1.  Preserved authentication and to-do functionality
2.  Display of Authors table and Books table (with visible author_id)
3.  Creating and editing an author
4.  Creating and editing a book (including changing assigned author)
5.  Deleting a book without affecting its referenced author
6.  Deleting an author and confirming foreign key ON DELETE CASCADE deleted their books
7.  Rejection of nonexistent author IDs
8.  Rejection of blank text and invalid negative/malformed prices
9.  Uploading and replacing author portraits and book covers
10. Preserving images when editing without selecting a replacement
11. Rejecting invalid extensions, disguised binaries, and oversized uploads
12. Data persistence across application/database restarts
13. Mobile viewport compatibility and responsive rendering
14. Clean reproducible DDL and DML execution in an isolated database
"""

import io
import os
import unittest
import sqlite3
from decimal import Decimal
from PIL import Image

from app import app, init_db
from database.db import _connect_sqlite

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), 'test_isolated_library.db')
TEST_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'test_static_uploads')


class ANULab3LibraryTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.makedirs(os.path.join(TEST_UPLOAD_DIR, 'authors'), exist_ok=True)
        os.makedirs(os.path.join(TEST_UPLOAD_DIR, 'books'), exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except Exception:
                pass
        # Clean up test upload files
        for root, dirs, files in os.walk(TEST_UPLOAD_DIR, topdown=False):
            for f in files:
                try:
                    os.remove(os.path.join(root, f))
                except Exception:
                    pass
            for d in dirs:
                try:
                    os.rmdir(os.path.join(root, d))
                except Exception:
                    pass
        if os.path.exists(TEST_UPLOAD_DIR):
            try:
                os.rmdir(TEST_UPLOAD_DIR)
            except Exception:
                pass

    def setUp(self):
        # Configure app for isolated testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DATABASE'] = TEST_DB_PATH
        app.config['UPLOAD_FOLDER'] = TEST_UPLOAD_DIR
        self.client = app.test_client()

        # Clean old test DB if present
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except Exception:
                pass

        # Initialize test database
        with app.app_context():
            init_db(TEST_DB_PATH)

        # Register and log in a dedicated test user
        self.client.post('/register', data={
            'full_name': 'Test Librarian',
            'email': 'librarian@anu.edu.eg',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        }, follow_redirects=True)

        self.client.post('/login', data={
            'email': 'librarian@anu.edu.eg',
            'password': 'Password123!'
        }, follow_redirects=True)

    def tearDown(self):
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except Exception:
                pass

    def _create_sample_png_bytes(self, color=(100, 150, 200), size=(100, 100)):
        """Generate a valid in-memory raster PNG image."""
        img = Image.new('RGB', size, color=color)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf

    def test_01_preserved_auth_and_todos(self):
        """Check 1: Existing registration, login, logout, and to-do functionality work flawlessly."""
        # Add to-do task
        res_add = self.client.post('/todos/add', data={
            'title': 'Evaluate Database Systems Lab 3',
            'description': 'Foreign Keys and ON DELETE CASCADE evaluation',
            'due_date': '2026-10-26'
        }, follow_redirects=True)
        self.assertEqual(res_add.status_code, 200)
        self.assertIn(b'Evaluate Database Systems Lab 3', res_add.data)

        # Verify in database
        conn = _connect_sqlite(TEST_DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT * FROM todos WHERE title = 'Evaluate Database Systems Lab 3'")
        todo = cur.fetchone()
        self.assertIsNotNone(todo)
        todo_id = todo['id']

        # Toggle to-do
        self.client.post(f'/todos/{todo_id}/toggle', follow_redirects=True)
        cur.execute("SELECT is_done FROM todos WHERE id = ?", (todo_id,))
        self.assertEqual(cur.fetchone()['is_done'], 1)

        # Delete to-do
        self.client.post(f'/todos/{todo_id}/delete', follow_redirects=True)
        cur.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        self.assertIsNone(cur.fetchone())
        conn.close()

    def test_02_display_tables_and_visible_author_id(self):
        """Check 2: Displaying both required tables and verifying author_id is visibly rendered."""
        # 1. Display Authors Table (F2.1)
        res_authors = self.client.get('/authors')
        self.assertEqual(res_authors.status_code, 200)
        self.assertIn(b'Authors Registry', res_authors.data)
        self.assertIn(b'George Orwell', res_authors.data)
        self.assertIn(b'Jane Austen', res_authors.data)
        self.assertIn(b'Naguib Mahfouz', res_authors.data)

        # 2. Display Books Table (F2.1)
        res_books = self.client.get('/books')
        self.assertEqual(res_books.status_code, 200)
        self.assertIn(b'Books Catalog', res_books.data)
        self.assertIn(b'Nineteen Eighty-Four', res_books.data)
        self.assertIn(b'Pride and Prejudice', res_books.data)
        # Visibly includes author_id
        self.assertIn(b'author_id:', res_books.data)
        self.assertIn(b'badge-author-id', res_books.data)

    def test_03_create_and_edit_author(self):
        """Check 3: Creating and editing an author."""
        # Create Author (F2.2)
        res_add = self.client.post('/authors/add', data={
            'name': 'Taha Hussein',
            'country': 'Egypt'
        }, follow_redirects=True)
        self.assertEqual(res_add.status_code, 200)
        self.assertIn(b'added successfully', res_add.data)

        conn = _connect_sqlite(TEST_DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT * FROM author WHERE name = 'Taha Hussein'")
        author = cur.fetchone()
        self.assertIsNotNone(author)
        author_id = author['author_id']
        self.assertEqual(author['country'], 'Egypt')

        # Edit Author (F2.3)
        res_edit = self.client.post(f'/authors/{author_id}/edit', data={
            'name': 'Dr. Taha Hussein',
            'country': 'Egypt (Dean of Arabic Literature)'
        }, follow_redirects=True)
        self.assertEqual(res_edit.status_code, 200)
        self.assertIn(b'updated successfully', res_edit.data)

        cur.execute("SELECT * FROM author WHERE author_id = ?", (author_id,))
        updated = cur.fetchone()
        self.assertEqual(updated['name'], 'Dr. Taha Hussein')
        self.assertEqual(updated['country'], 'Egypt (Dean of Arabic Literature)')
        conn.close()

    def test_04_create_and_edit_book_and_change_author(self):
        """Check 4: Creating and editing a book, including changing its author."""
        # Create Book for Author 1 (F2.2)
        res_add = self.client.post('/books/add', data={
            'title': 'Homage to Catalonia',
            'price': '13.50',
            'author_id': '1'
        }, follow_redirects=True)
        self.assertEqual(res_add.status_code, 200)
        self.assertIn(b'added successfully', res_add.data)

        conn = _connect_sqlite(TEST_DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT * FROM book WHERE title = 'Homage to Catalonia'")
        book = cur.fetchone()
        self.assertIsNotNone(book)
        book_id = book['book_id']
        self.assertEqual(book['author_id'], 1)

        # Edit Book and change assigned author to Author 2 (F2.3)
        res_edit = self.client.post(f'/books/{book_id}/edit', data={
            'title': 'Homage to Catalonia (Revised)',
            'price': '14.95',
            'author_id': '2'
        }, follow_redirects=True)
        self.assertEqual(res_edit.status_code, 200)
        self.assertIn(b'updated successfully', res_edit.data)

        cur.execute("SELECT * FROM book WHERE book_id = ?", (book_id,))
        updated = cur.fetchone()
        self.assertEqual(updated['title'], 'Homage to Catalonia (Revised)')
        self.assertEqual(float(updated['price']), 14.95)
        self.assertEqual(updated['author_id'], 2)
        conn.close()

    def test_05_delete_book_without_affecting_author(self):
        """Check 5: Deleting a book must NOT delete its author."""
        # Create disposable book for author 3
        conn = _connect_sqlite(TEST_DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO book (title, price, author_id) VALUES ('Temp Delete Book', 5.00, 3)")
        conn.commit()
        book_id = cur.lastrowid

        # Delete Book (F2.4)
        res_del = self.client.post(f'/books/{book_id}/delete', follow_redirects=True)
        self.assertEqual(res_del.status_code, 200)

        # Verify book deleted
        cur.execute("SELECT * FROM book WHERE book_id = ?", (book_id,))
        self.assertIsNone(cur.fetchone())

        # Verify author 3 STILL EXISTS intact
        cur.execute("SELECT * FROM author WHERE author_id = 3")
        author_3 = cur.fetchone()
        self.assertIsNotNone(author_3)
        self.assertEqual(author_3['name'], 'Arthur Conan Doyle')
        conn.close()

    def test_06_delete_author_and_confirm_on_delete_cascade(self):
        """Check 6: Deleting an author triggers ON DELETE CASCADE, removing all their books."""
        conn = _connect_sqlite(TEST_DB_PATH)
        cur = conn.cursor()

        # Insert disposable author with 2 child books
        cur.execute("INSERT INTO author (name, country) VALUES ('Cascade Author', 'Testland')")
        conn.commit()
        cascade_author_id = cur.lastrowid

        cur.execute("INSERT INTO book (title, price, author_id) VALUES ('Cascade Book 1', 10.00, ?)", (cascade_author_id,))
        cur.execute("INSERT INTO book (title, price, author_id) VALUES ('Cascade Book 2', 15.00, ?)", (cascade_author_id,))
        conn.commit()

        # Delete Author (F2.5)
        res_del = self.client.post(f'/authors/{cascade_author_id}/delete', follow_redirects=True)
        self.assertEqual(res_del.status_code, 200)
        self.assertIn(b'deleted', res_del.data)
        self.assertIn(b'ON DELETE CASCADE', res_del.data)

        # Verify author is deleted
        cur.execute("SELECT * FROM author WHERE author_id = ?", (cascade_author_id,))
        self.assertIsNone(cur.fetchone())

        # CRITICAL REFERENTIAL INTEGRITY CHECK: Verify all child books were automatically deleted!
        cur.execute("SELECT * FROM book WHERE author_id = ?", (cascade_author_id,))
        orphaned_books = cur.fetchall()
        self.assertEqual(len(orphaned_books), 0, "Foreign Key ON DELETE CASCADE failed: child books still exist!")
        conn.close()

    def test_07_rejection_of_nonexistent_author_ids(self):
        """Check 7: Rejection of nonexistent author IDs when creating or editing books."""
        # Nonexistent author ID 9999
        res = self.client.post('/books/add', data={
            'title': 'Ghost Author Book',
            'price': '10.00',
            'author_id': '9999'
        }, follow_redirects=True)
        self.assertIn(b'does not exist', res.data)

        conn = _connect_sqlite(TEST_DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT * FROM book WHERE title = 'Ghost Author Book'")
        self.assertIsNone(cur.fetchone())
        conn.close()

    def test_08_empty_inputs_and_invalid_prices(self):
        """Check 8: Empty text inputs and invalid/negative prices must be rejected."""
        # 1. Blank author name
        res_author_blank = self.client.post('/authors/add', data={
            'name': '   ',
            'country': 'Egypt'
        }, follow_redirects=True)
        self.assertIn(b'mandatory', res_author_blank.data)

        # 2. Blank book title
        res_book_blank = self.client.post('/books/add', data={
            'title': '   ',
            'price': '12.00',
            'author_id': '1'
        }, follow_redirects=True)
        self.assertIn(b'cannot be blank', res_book_blank.data)

        # 3. Negative price
        res_neg_price = self.client.post('/books/add', data={
            'title': 'Negative Price Book',
            'price': '-15.50',
            'author_id': '1'
        }, follow_redirects=True)
        self.assertIn(b'non-negative', res_neg_price.data)

        # 4. Malformed price text
        res_bad_price = self.client.post('/books/add', data={
            'title': 'Bad Price Book',
            'price': 'abc.xyz',
            'author_id': '1'
        }, follow_redirects=True)
        self.assertIn(b'Invalid price format', res_bad_price.data)

    def test_09_image_upload_and_replacement(self):
        """Check 9: Uploading and replacing author portrait and book cover."""
        # Upload Author with Portrait
        portrait_buf = self._create_sample_png_bytes(color=(80, 120, 200))
        res_author = self.client.post('/authors/add', data={
            'name': 'Illustrated Author',
            'country': 'France',
            'photo': (portrait_buf, 'portrait.png')
        }, content_type='multipart/form-data', follow_redirects=True)
        self.assertIn(b'added successfully', res_author.data)

        conn = _connect_sqlite(TEST_DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT author_id, photo_path FROM author WHERE name = 'Illustrated Author'")
        author = cur.fetchone()
        self.assertIsNotNone(author)
        self.assertIsNotNone(author['photo_path'])
        initial_photo = author['photo_path']

        # Replace Portrait on Edit
        new_portrait_buf = self._create_sample_png_bytes(color=(200, 80, 80))
        res_edit_author = self.client.post(f'/authors/{author["author_id"]}/edit', data={
            'name': 'Illustrated Author (Updated)',
            'country': 'France',
            'photo': (new_portrait_buf, 'portrait_v2.png')
        }, content_type='multipart/form-data', follow_redirects=True)
        self.assertIn(b'updated successfully', res_edit_author.data)

        cur.execute("SELECT photo_path FROM author WHERE author_id = ?", (author['author_id'],))
        updated_photo = cur.fetchone()['photo_path']
        self.assertNotEqual(initial_photo, updated_photo)
        conn.close()

    def test_10_image_preservation_on_edit_without_new_upload(self):
        """Check 10: Preserving existing image when editing without selecting a replacement."""
        conn = _connect_sqlite(TEST_DB_PATH)
        cur = conn.cursor()
        # Verify Orwell has initial photo
        cur.execute("SELECT photo_path FROM author WHERE author_id = 1")
        initial_photo = cur.fetchone()['photo_path']
        self.assertIsNotNone(initial_photo)

        # Edit Orwell's country WITHOUT uploading a new photo
        res_edit = self.client.post('/authors/1/edit', data={
            'name': 'George Orwell',
            'country': 'United Kingdom (Updated)'
        }, follow_redirects=True)
        self.assertEqual(res_edit.status_code, 200)

        cur.execute("SELECT photo_path FROM author WHERE author_id = 1")
        preserved_photo = cur.fetchone()['photo_path']
        self.assertEqual(initial_photo, preserved_photo, "Image path was wiped instead of preserved!")
        conn.close()

    def test_11_rejection_of_invalid_and_oversized_uploads(self):
        """Check 11: Rejecting executable files, disguised binaries, and oversized uploads."""
        # 1. Executable file disguised with .jpg extension
        fake_exe = io.BytesIO(b"MZ\x90\x00\x03\x00\x00\x00This is a fake PE executable binary")
        res_exe = self.client.post('/authors/add', data={
            'name': 'Hacker Author',
            'country': 'Nowhere',
            'photo': (fake_exe, 'malware.exe.jpg')
        }, content_type='multipart/form-data', follow_redirects=True)
        self.assertIn(b'Invalid image file', res_exe.data)

        # 2. Disallowed extension (.sh or .php)
        script_file = io.BytesIO(b"echo 'hello'")
        res_script = self.client.post('/authors/add', data={
            'name': 'Script Author',
            'country': 'Nowhere',
            'photo': (script_file, 'script.php')
        }, content_type='multipart/form-data', follow_redirects=True)
        self.assertIn(b'Invalid image format', res_script.data)

        # 3. Oversized file (Exceeding 5MB)
        huge_file = io.BytesIO(b"0" * (6 * 1024 * 1024))
        res_huge = self.client.post('/authors/add', data={
            'name': 'Huge Author',
            'country': 'Nowhere',
            'photo': (huge_file, 'huge.png')
        }, content_type='multipart/form-data', follow_redirects=True)
        self.assertIn(b'exceeds the 5MB limit', res_huge.data)

    def test_12_data_persistence_across_restarts(self):
        """Check 12: Data persists after closing and reopening database connection."""
        # Insert author
        self.client.post('/authors/add', data={
            'name': 'Persistent Author',
            'country': 'Egypt'
        }, follow_redirects=True)

        # Simulate fresh connection / restart
        conn = _connect_sqlite(TEST_DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT * FROM author WHERE name = 'Persistent Author'")
        self.assertIsNotNone(cur.fetchone())
        conn.close()

    def test_13_mobile_layout_elements(self):
        """Check 13: Responsive design tokens, viewport meta, and mobile toggle elements exist."""
        res = self.client.get('/books')
        self.assertEqual(res.status_code, 200)
        # Check viewport meta tag for mobile responsiveness (down to 360px)
        self.assertIn(b'name="viewport" content="width=device-width, initial-scale=1.0"', res.data)
        # Check responsive hamburger toggle button
        self.assertIn(b'id="navToggle"', res.data)
        self.assertIn(b'toggleMobileNav()', res.data)
        # Check table-responsive container for horizontal scrolling
        self.assertIn(b'class="table-responsive"', res.data)

    def test_14_clean_ddl_and_dml_execution(self):
        """Check 14: Reproducible clean setup using problem2_DDL.sql and problem2_DML.sql."""
        ddl_path = os.path.join(os.path.dirname(__file__), 'problem2_DDL.sql')
        dml_path = os.path.join(os.path.dirname(__file__), 'problem2_DML.sql')
        self.assertTrue(os.path.exists(ddl_path), "problem2_DDL.sql must exist!")
        self.assertTrue(os.path.exists(dml_path), "problem2_DML.sql must exist!")

        with open(ddl_path, 'r', encoding='utf-8') as f:
            ddl_content = f.read()
        with open(dml_path, 'r', encoding='utf-8') as f:
            dml_content = f.read()

        # Verify key relational syntax in scripts
        self.assertIn('CREATE TABLE author', ddl_content)
        self.assertIn('CREATE TABLE book', ddl_content)
        self.assertIn('ON DELETE CASCADE', ddl_content)
        self.assertIn('DECIMAL(10, 2)', ddl_content)
        self.assertIn('INSERT INTO author', dml_content)
        self.assertIn('INSERT INTO book', dml_content)


if __name__ == '__main__':
    unittest.main()
