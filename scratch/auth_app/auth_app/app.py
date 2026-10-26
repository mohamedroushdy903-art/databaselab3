import os
import re
import sqlite3
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    g
)
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = os.path.join(os.path.dirname(__file__), 'users.db')

app = Flask(__name__)
# Secret key for session signing (persistent across restarts)
app.secret_key = os.environ.get('SECRET_KEY', 'super-secret-auth-key-2026-antigravity')

def get_db():
    """Get database connection for the current request context."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """Close the database at the end of request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize SQLite database tables from schema.sql."""
    db = sqlite3.connect(DATABASE)
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())
    db.commit()
    db.close()

# Initialize DB on application startup
with app.app_context():
    init_db()

def login_required(f):
    """Decorator to require login for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
        # Parameterized query to prevent SQL injection
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_email'] = user['email']
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
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

        # Server-side validations
        if not full_name or not email or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('register.html', full_name=full_name, email=email)

        # Basic email format check
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

        # Check for existing email
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            flash('An account with this email address already exists.', 'danger')
            return render_template('register.html', full_name=full_name, email=email)

        # Hash password securely
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        try:
            cursor.execute(
                "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
                (full_name, email, password_hash)
            )
            db.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('An account with this email address already exists.', 'danger')
            return render_template('register.html', full_name=full_name, email=email)

    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, full_name, email, created_at FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()

    if not user:
        session.clear()
        flash('User session expired. Please log in again.', 'warning')
        return redirect(url_for('login'))

    return render_template('dashboard.html', user=user)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("Launching Authentication App on http://127.0.0.1:5000 ...")
    app.run(debug=True, port=5000)
