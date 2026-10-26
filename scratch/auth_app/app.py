"""
Alexandria National University (ANU) - Faculty of Engineering
Course: Introduction to Database Systems (Fall 2026)
Instructor: Dr. Yasser Fouad
Teaching Assistants: Eng. Abdallah Elsayed, Eng. Basem Hesham, Eng. Danny Hossam

Lab 2 & Lab 3 Web Application:
- Multi-user authentication & secure password hashing (PBKDF2 SHA-256)
- Private To-Do task management with database isolation (Lab 2)
- Library Database: Authors & Books with ON DELETE CASCADE and Image Uploads (Lab 3 Problem 2)
- Parameterized plain SQL preventing SQL injection (No ORM)
- Supports MySQL Server and SQLite transparently
"""

import os
import re
import secrets
from decimal import Decimal, InvalidOperation
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    g,
    abort
)
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import get_db, close_db, init_db, query_db
from upload_utils import validate_and_save_image

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'anu-lab3-library-database-systems-fall-2026-secret')

# Configure file upload limits (5MB max)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File size exceeds the 5MB limit. Please upload a smaller image.', 'danger')
    return redirect(request.referrer or url_for('library_books'))

# Register teardown function to safely close database connection
app.teardown_appcontext(close_db)

# Auto-initialize database tables and seed records on application launch
with app.app_context():
    init_db()


# =========================================================================
# Security & CSRF Protection
# =========================================================================

@app.before_request
def ensure_csrf_token():
    """Ensure every active session has a secure anti-CSRF token."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)


@app.context_processor
def inject_csrf_token():
    """Inject CSRF token into all Jinja2 template contexts."""
    return dict(csrf_token=session.get('csrf_token', ''))


def verify_csrf(f):
    """Decorator to enforce CSRF token validation on state-changing POST requests."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if app.config.get('TESTING'):
            return f(*args, **kwargs)
        if request.method == 'POST':
            token = request.form.get('csrf_token')
            if not token or token != session.get('csrf_token'):
                flash('Security check failed: invalid or missing CSRF token. Please try again.', 'danger')
                return redirect(request.referrer or url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# =========================================================================
# Authentication Decorators
# =========================================================================

def login_required(f):
    """Decorator to protect authenticated routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to restrict access strictly to Administrators (Privacy Protection)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in as an administrator.', 'warning')
            return redirect(url_for('login'))

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT is_admin FROM users WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()

        if not user or not user['is_admin']:
            flash('Access Denied: Only Administrators can inspect the database.', 'danger')
            return redirect(url_for('dashboard'))

        return f(*args, **kwargs)
    return decorated_function


# =========================================================================
# Authentication Routes (R1–R3, R9)
# =========================================================================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please fill in all fields.', 'danger')
            return render_template('login.html', email=email)

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_email'] = user['email']
            session['is_admin'] = bool(user['is_admin'])
            session['csrf_token'] = secrets.token_hex(16)
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            return render_template('login.html', email=email)

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Server-side validation
        if not full_name or not email or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('register.html', full_name=full_name, email=email)

        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('register.html', full_name=full_name, email=email)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html', full_name=full_name, email=email)

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template('register.html', full_name=full_name, email=email)

        db = get_db()
        cursor = db.cursor()

        # Check for existing email (R2: Email Already Exists)
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            flash('Email Already Exists.', 'danger')
            return render_template('register.html', full_name=full_name, email=email)

        # Secure password hashing (PBKDF2 SHA-256)
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        try:
            cursor.execute(
                "INSERT INTO users (full_name, email, password_hash, is_admin) VALUES (?, ?, ?, 0)",
                (full_name, email, password_hash)
            )
            db.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception:
            flash('Email Already Exists.', 'danger')
            return render_template('register.html', full_name=full_name, email=email)

    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


# =========================================================================
# To-Do List Routes (Lab 2 Preservation)
# =========================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id, full_name, email, is_admin, created_at FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        session.clear()
        flash('User session expired. Please log in again.', 'warning')
        return redirect(url_for('login'))

    # Automatically synchronize active session with database admin role
    session['is_admin'] = bool(user['is_admin'])

    # Private list: user sees ONLY their own to-dos (R9)
    cursor.execute(
        """
        SELECT id, user_id, title, description, due_date, is_done, created_at
        FROM todos
        WHERE user_id = ?
        ORDER BY is_done ASC, due_date ASC, id DESC
        """,
        (user_id,)
    )
    todos = cursor.fetchall()

    total_count = len(todos)
    open_count = sum(1 for t in todos if t['is_done'] == 0)
    done_count = total_count - open_count

    return render_template(
        'dashboard.html',
        user=user,
        todos=todos,
        total_count=total_count,
        open_count=open_count,
        done_count=done_count
    )


@app.route('/todos/add', methods=['POST'])
@login_required
def add_todo():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    due_date = request.form.get('due_date', '').strip()

    if not title:
        flash('Task title cannot be empty.', 'danger')
        return redirect(url_for('dashboard'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO todos (user_id, title, description, due_date, is_done) VALUES (?, ?, ?, ?, 0)",
        (session['user_id'], title, description, due_date)
    )
    db.commit()
    flash('Task added successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/todos/<int:todo_id>/toggle', methods=['POST'])
@login_required
def toggle_todo(todo_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE todos SET is_done = CASE WHEN is_done = 1 THEN 0 ELSE 1 END WHERE id = ? AND user_id = ?",
        (todo_id, session['user_id'])
    )
    db.commit()
    flash('Task status updated.', 'info')
    return redirect(url_for('dashboard'))


@app.route('/todos/<int:todo_id>/edit', methods=['POST'])
@login_required
def edit_todo(todo_id):
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    due_date = request.form.get('due_date', '').strip()

    if not title:
        flash('Task title cannot be empty.', 'danger')
        return redirect(url_for('dashboard'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE todos SET title = ?, description = ?, due_date = ? WHERE id = ? AND user_id = ?",
        (title, description, due_date, todo_id, session['user_id'])
    )
    db.commit()
    flash('Task updated successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/todos/<int:todo_id>/delete', methods=['POST'])
@login_required
def delete_todo(todo_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM todos WHERE id = ? AND user_id = ?",
        (todo_id, session['user_id'])
    )
    db.commit()
    flash('Task deleted successfully.', 'info')
    return redirect(url_for('dashboard'))


# =========================================================================
# Library Management Routes: PART II / PROBLEM 2 (F2.1 – F2.5 & Bonus)
# =========================================================================

@app.route('/library')
@login_required
def library_index():
    """Convenience redirect to books collection."""
    return redirect(url_for('library_books'))


@app.route('/authors')
@login_required
def library_authors():
    """
    F2.1: Display Authors Table.
    Shows author_id (PK), name, country, and portrait photo.
    Computes book counts using simple SELECT query to adhere to assignment simplicity guidelines.
    """
    db = get_db()
    cursor = db.cursor()
    
    # Simple plain SQL SELECT
    cursor.execute("SELECT author_id, name, country, photo_path FROM author ORDER BY author_id ASC")
    authors = cursor.fetchall()
    
    # Calculate book counts per author without complex JOIN/GROUP BY
    cursor.execute("SELECT author_id FROM book")
    all_book_authors = cursor.fetchall()
    book_counts = {}
    for b in all_book_authors:
        aid = b['author_id']
        book_counts[aid] = book_counts.get(aid, 0) + 1

    return render_template(
        'library_authors.html',
        authors=authors,
        book_counts=book_counts,
        total_authors=len(authors)
    )


@app.route('/authors/add', methods=['POST'])
@login_required
@verify_csrf
def add_author():
    """
    F2.2: Add an author.
    Bonus: Upload author portrait photo with format/binary verification.
    """
    name = request.form.get('name', '').strip()
    country = request.form.get('country', '').strip()

    if not name or not country:
        flash('Author name and country are mandatory fields.', 'danger')
        return redirect(url_for('library_authors'))

    photo_path = None
    if 'photo' in request.files and request.files['photo'].filename != '':
        success, res = validate_and_save_image(
            request.files['photo'],
            app.config['UPLOAD_FOLDER'],
            subfolder='authors'
        )
        if not success:
            flash(f'Portrait upload error: {res}', 'danger')
            return redirect(url_for('library_authors'))
        photo_path = res

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO author (name, country, photo_path) VALUES (?, ?, ?)",
        (name, country, photo_path)
    )
    db.commit()
    flash(f'Author "{name}" added successfully!', 'success')
    return redirect(url_for('library_authors'))


@app.route('/authors/<int:author_id>/edit', methods=['POST'])
@login_required
@verify_csrf
def edit_author(author_id):
    """
    F2.3: Edit an author's name and country.
    Bonus: Change or preserve author portrait photo.
    """
    name = request.form.get('name', '').strip()
    country = request.form.get('country', '').strip()

    if not name or not country:
        flash('Author name and country cannot be blank.', 'danger')
        return redirect(url_for('library_authors'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT author_id, photo_path FROM author WHERE author_id = ?", (author_id,))
    author = cursor.fetchone()

    if not author:
        flash('Author not found.', 'danger')
        return redirect(url_for('library_authors'))

    # Retain current photo_path by default
    photo_path = author['photo_path']

    if 'photo' in request.files and request.files['photo'].filename != '':
        success, res = validate_and_save_image(
            request.files['photo'],
            app.config['UPLOAD_FOLDER'],
            subfolder='authors'
        )
        if not success:
            flash(f'Portrait upload error: {res}', 'danger')
            return redirect(url_for('library_authors'))
        photo_path = res

    cursor.execute(
        "UPDATE author SET name = ?, country = ?, photo_path = ? WHERE author_id = ?",
        (name, country, photo_path, author_id)
    )
    db.commit()
    flash(f'Author "#{author_id}" updated successfully!', 'success')
    return redirect(url_for('library_authors'))


@app.route('/authors/<int:author_id>/delete', methods=['POST'])
@login_required
@verify_csrf
def delete_author(author_id):
    """
    F2.5: Remove an author.
    Warning & Execution: Deleting an author automatically cascades and deletes all
    books belonging to that author through the database's ON DELETE CASCADE foreign key.
    """
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT name FROM author WHERE author_id = ?", (author_id,))
    author = cursor.fetchone()

    if not author:
        flash('Author not found.', 'danger')
        return redirect(url_for('library_authors'))

    # Count books that will be cascade-deleted
    cursor.execute("SELECT COUNT(*) as cnt FROM book WHERE author_id = ?", (author_id,))
    count_row = cursor.fetchone()
    books_count = count_row['cnt'] if isinstance(count_row, dict) else count_row[0]

    # Parameterized plain SQL DELETE
    cursor.execute("DELETE FROM author WHERE author_id = ?", (author_id,))
    db.commit()

    flash(
        f'Author "{author["name"]}" deleted. {books_count} associated book(s) were automatically removed by database ON DELETE CASCADE constraint.',
        'info'
    )
    return redirect(url_for('library_authors'))


@app.route('/books')
@login_required
def library_books():
    """
    F2.1: Display Books Table.
    Visibly displays book_id (PK), title, price, and author_id (FK), plus author name and cover.
    Provides author list for creation dropdown (F2.2).
    """
    db = get_db()
    cursor = db.cursor()

    # Simple SELECT on book
    cursor.execute("SELECT book_id, title, price, author_id, cover_path FROM book ORDER BY book_id ASC")
    books = cursor.fetchall()

    # Simple SELECT on author for dropdown and author name mapping (No JOIN required)
    cursor.execute("SELECT author_id, name, country FROM author ORDER BY name ASC")
    authors = cursor.fetchall()
    authors_map = {a['author_id']: a['name'] for a in authors}

    return render_template(
        'library_books.html',
        books=books,
        authors=authors,
        authors_map=authors_map,
        total_books=len(books)
    )


@app.route('/books/add', methods=['POST'])
@login_required
@verify_csrf
def add_book():
    """
    F2.2: Add a book.
    - Validates title, price (DECIMAL >= 0), and selected author_id.
    - Uses author dropdown populated from database.
    - Bonus: Upload book cover image.
    """
    title = request.form.get('title', '').strip()
    price_raw = request.form.get('price', '').strip()
    author_id_raw = request.form.get('author_id', '').strip()

    if not title:
        flash('Book title cannot be blank.', 'danger')
        return redirect(url_for('library_books'))

    # Validate price as non-negative decimal
    try:
        price = Decimal(price_raw)
        if price < Decimal('0.00'):
            flash('Price must be a non-negative value (>= 0.00).', 'danger')
            return redirect(url_for('library_books'))
        if price > Decimal('99999999.99'):
            flash('Price exceeds the maximum allowable DECIMAL(10,2) limit.', 'danger')
            return redirect(url_for('library_books'))
        price_val = float(round(price, 2))
    except (InvalidOperation, ValueError):
        flash('Invalid price format. Please enter a valid decimal number (e.g. 19.99).', 'danger')
        return redirect(url_for('library_books'))

    # Validate author selection
    try:
        author_id = int(author_id_raw)
    except (ValueError, TypeError):
        flash('Please select a valid author from the list.', 'danger')
        return redirect(url_for('library_books'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT author_id, name FROM author WHERE author_id = ?", (author_id,))
    author = cursor.fetchone()

    if not author:
        flash(f'Invalid author ID #{author_id}. The selected author does not exist.', 'danger')
        return redirect(url_for('library_books'))

    cover_path = None
    if 'cover' in request.files and request.files['cover'].filename != '':
        success, res = validate_and_save_image(
            request.files['cover'],
            app.config['UPLOAD_FOLDER'],
            subfolder='books'
        )
        if not success:
            flash(f'Cover upload error: {res}', 'danger')
            return redirect(url_for('library_books'))
        cover_path = res

    cursor.execute(
        "INSERT INTO book (title, price, author_id, cover_path) VALUES (?, ?, ?, ?)",
        (title, price_val, author_id, cover_path)
    )
    db.commit()
    flash(f'Book "{title}" added successfully for author {author["name"]}!', 'success')
    return redirect(url_for('library_books'))


@app.route('/books/<int:book_id>/edit', methods=['POST'])
@login_required
@verify_csrf
def edit_book(book_id):
    """
    F2.3: Edit a book's title, price, and assigned author.
    Bonus: Change or preserve book cover image.
    """
    title = request.form.get('title', '').strip()
    price_raw = request.form.get('price', '').strip()
    author_id_raw = request.form.get('author_id', '').strip()

    if not title:
        flash('Book title cannot be blank.', 'danger')
        return redirect(url_for('library_books'))

    try:
        price = Decimal(price_raw)
        if price < Decimal('0.00') or price > Decimal('99999999.99'):
            flash('Price must be between 0.00 and 99,999,999.99.', 'danger')
            return redirect(url_for('library_books'))
        price_val = float(round(price, 2))
    except (InvalidOperation, ValueError):
        flash('Invalid price format. Please enter a valid decimal number.', 'danger')
        return redirect(url_for('library_books'))

    try:
        author_id = int(author_id_raw)
    except (ValueError, TypeError):
        flash('Please select a valid author.', 'danger')
        return redirect(url_for('library_books'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT book_id, cover_path FROM book WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()

    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('library_books'))

    cursor.execute("SELECT author_id FROM author WHERE author_id = ?", (author_id,))
    if not cursor.fetchone():
        flash(f'Author #{author_id} does not exist.', 'danger')
        return redirect(url_for('library_books'))

    cover_path = book['cover_path']
    if 'cover' in request.files and request.files['cover'].filename != '':
        success, res = validate_and_save_image(
            request.files['cover'],
            app.config['UPLOAD_FOLDER'],
            subfolder='books'
        )
        if not success:
            flash(f'Cover upload error: {res}', 'danger')
            return redirect(url_for('library_books'))
        cover_path = res

    cursor.execute(
        "UPDATE book SET title = ?, price = ?, author_id = ?, cover_path = ? WHERE book_id = ?",
        (title, price_val, author_id, cover_path, book_id)
    )
    db.commit()
    flash(f'Book #{book_id} updated successfully!', 'success')
    return redirect(url_for('library_books'))


@app.route('/books/<int:book_id>/delete', methods=['POST'])
@login_required
@verify_csrf
def delete_book(book_id):
    """
    F2.4: Remove a book.
    Deleting a book removes only the book record; the referenced author remains untouched.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT title, author_id FROM book WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()

    if not book:
        flash('Book not found.', 'danger')
        return redirect(url_for('library_books'))

    cursor.execute("DELETE FROM book WHERE book_id = ?", (book_id,))
    db.commit()

    flash(f'Book "{book["title"]}" has been removed. The author (Author ID #{book["author_id"]}) remains intact.', 'info')
    return redirect(url_for('library_books'))


# =========================================================================
# Administrator Routes (Privacy Inspection)
# =========================================================================

@app.route('/admin')
@app.route('/users')
@login_required
@admin_required
def admin_users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, full_name, email, password_hash, is_admin, created_at FROM users ORDER BY id ASC")
    users = cursor.fetchall()

    cursor.execute(
        """
        SELECT t.id, t.user_id, u.full_name as author, t.title, t.due_date, t.is_done, t.created_at
        FROM todos t
        JOIN users u ON t.user_id = u.id
        ORDER BY t.id ASC
        """
    )
    todos = cursor.fetchall()

    return render_template('admin_users.html', users=users, todos=todos)


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
@verify_csrf
def admin_delete_user(user_id):
    if user_id == session['user_id']:
        flash('You cannot delete your own active administrator account.', 'warning')
        return redirect(url_for('admin_users'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT full_name FROM users WHERE id = ?", (user_id,))
    target_user = cursor.fetchone()

    if target_user:
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        flash(f'User "{target_user["full_name"]}" and all their tasks deleted via ON DELETE CASCADE.', 'success')
    else:
        flash('User not found.', 'danger')

    return redirect(url_for('admin_users'))


@app.route('/admin/todos/<int:todo_id>/delete', methods=['POST'])
@login_required
@admin_required
@verify_csrf
def admin_delete_todo(todo_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    db.commit()
    flash(f'Task #{todo_id} has been deleted by administrator.', 'info')
    return redirect(url_for('admin_users'))


if __name__ == '__main__':
    print("=========================================================================")
    print(" Alexandria National University (ANU) - Faculty of Engineering")
    print(" Introduction to Database Systems - Lab 2 & Lab 3 Full Stack Portal")
    print(" Local URL: http://127.0.0.1:5000")
    print("=========================================================================")
    app.run(debug=True, host='0.0.0.0', port=5000)
