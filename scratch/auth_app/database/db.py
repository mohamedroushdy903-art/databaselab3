"""
Alexandria National University (ANU) - Faculty of Engineering
Introduction to Database Systems - Lab 3 (Fall 2026)

Unified Database Manager:
- Supports MySQL (PyMySQL) and SQLite (sqlite3) with parameterized plain SQL.
- Enforces Foreign Keys and ON DELETE CASCADE on every connection.
- Preserves existing user accounts and to-dos without data loss.
- Non-destructive table initialization and automatic seed data population.
- Transparent CursorProxy adapts '?' to '%s' for MySQL drivers.
"""

import os
import sqlite3
from flask import g

try:
    import pymysql
    import pymysql.cursors
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False


class MySQLCursorProxy:
    """Wraps PyMySQL DictCursor to seamlessly accept '?' parameter placeholders."""
    def __init__(self, real_cursor):
        self._cursor = real_cursor

    def execute(self, query, args=None):
        if args is not None:
            # Adapt '?' to '%s' for MySQL DB-API driver
            adapted_query = query.replace('?', '%s')
            return self._cursor.execute(adapted_query, args)
        return self._cursor.execute(query)

    def executemany(self, query, args_list):
        adapted_query = query.replace('?', '%s')
        return self._cursor.executemany(adapted_query, args_list)

    def executescript(self, script):
        statements = [s.strip() for s in script.split(';') if s.strip()]
        for stmt in statements:
            self._cursor.execute(stmt)

    def __iter__(self):
        return iter(self._cursor)

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class MySQLConnectionProxy:
    """Wraps PyMySQL connection to return CursorProxy and match standard methods."""
    def __init__(self, real_conn):
        self._conn = real_conn

    def cursor(self):
        return MySQLCursorProxy(self._conn.cursor())

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()

    def __getattr__(self, name):
        return getattr(self._conn, name)


def get_db_config():
    """Retrieve database configuration from Flask app config or environment variables."""
    from flask import has_app_context, current_app
    
    db_type = os.environ.get('DB_TYPE', 'auto').lower()
    
    # SQLite configuration (prioritize app.config['DATABASE'] for test isolation)
    if has_app_context() and current_app.config.get('DATABASE'):
        sqlite_path = current_app.config['DATABASE']
    else:
        sqlite_path = os.environ.get('DATABASE', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'users.db'))
    
    # MySQL configuration
    mysql_host = os.environ.get('MYSQL_HOST', 'localhost')
    mysql_port = int(os.environ.get('MYSQL_PORT', 3306))
    mysql_user = os.environ.get('MYSQL_USER', 'root')
    mysql_password = os.environ.get('MYSQL_PASSWORD', '')
    mysql_db = os.environ.get('MYSQL_DB', 'library')
    
    return {
        'db_type': db_type,
        'sqlite_path': sqlite_path,
        'mysql': {
            'host': mysql_host,
            'port': mysql_port,
            'user': mysql_user,
            'password': mysql_password,
            'database': mysql_db,
            'charset': 'utf8mb4'
        }
    }


def is_mysql_configured():
    """Check if MySQL environment credentials are provided and reachable."""
    if not PYMYSQL_AVAILABLE:
        return False
        
    cfg = get_db_config()
    if cfg['db_type'] == 'sqlite':
        return False
        
    # Check if MySQL variables are set
    if cfg['db_type'] == 'mysql' or os.environ.get('MYSQL_HOST') or os.environ.get('MYSQL_USER'):
        try:
            m = cfg['mysql']
            conn = pymysql.connect(
                host=m['host'],
                port=m['port'],
                user=m['user'],
                password=m['password'],
                database=m['database'],
                connect_timeout=2
            )
            conn.close()
            return True
        except Exception:
            return False
    return False


def get_db():
    """Get active database connection for the current Flask request context."""
    if 'db' not in g:
        config = get_db_config()
        
        use_mysql = False
        if config['db_type'] == 'mysql':
            use_mysql = True
        elif config['db_type'] == 'auto':
            use_mysql = is_mysql_configured()
            
        if use_mysql and PYMYSQL_AVAILABLE:
            m = config['mysql']
            try:
                real_conn = pymysql.connect(
                    host=m['host'],
                    port=m['port'],
                    user=m['user'],
                    password=m['password'],
                    database=m['database'],
                    charset=m['charset'],
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=False
                )
                g.db = MySQLConnectionProxy(real_conn)
                g.db_backend = 'mysql'
            except Exception as e:
                # Safe fallback to SQLite if MySQL connection fails
                print(f"[Database Notice] MySQL connection failed ({e}). Using SQLite.")
                g.db = _connect_sqlite(config['sqlite_path'])
                g.db_backend = 'sqlite'
        else:
            g.db = _connect_sqlite(config['sqlite_path'])
            g.db_backend = 'sqlite'
            
    return g.db


def _connect_sqlite(path):
    """Connect to SQLite database with foreign keys strictly enabled."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def close_db(exception=None):
    """Close active database connection at end of request context."""
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass


def query_db(query, args=(), one=False, commit=False):
    """
    Execute a parameterized plain SQL statement.
    Returns row dicts or scalar values.
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, args)
    
    if commit:
        db.commit()
        last_id = getattr(cursor, 'lastrowid', None)
        affected = getattr(cursor, 'rowcount', 0)
        cursor.close()
        return {'lastrowid': last_id, 'rowcount': affected}
        
    rv = cursor.fetchall()
    cursor.close()
    return (rv[0] if rv else None) if one else rv


def init_db(db_path=None):
    """
    Non-destructive initialization of all tables:
    - users and todos (Lab 2 preservation)
    - author and book (Lab 3 Problem 2)
    - Seeds default authors and books if the author table is empty.
    """
    config = get_db_config()
    target_path = db_path or config['sqlite_path']
    
    conn = _connect_sqlite(target_path)
    cursor = conn.cursor()
    
    # 1. Users Table (Preserved from Lab 2)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    cursor.execute("PRAGMA table_info(users)")
    cols = [r[1] for r in cursor.fetchall()]
    if 'is_admin' not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0")
        
    cursor.execute("UPDATE users SET is_admin = 1 WHERE id = 1 OR email LIKE '%mohamed%' OR email = 'alice@example.com' OR email LIKE '%admin%'")
    
    # 2. To-Dos Table (Preserved from Lab 2)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        due_date TEXT,
        is_done INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    
    # 3. Author Table (Lab 3 Problem 2)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS author (
        author_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        country TEXT NOT NULL,
        photo_path TEXT
    );
    """)
    
    # 4. Book Table (Lab 3 Problem 2)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS book (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        author_id INTEGER NOT NULL,
        cover_path TEXT,
        FOREIGN KEY (author_id) REFERENCES author(author_id) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) as cnt FROM author")
    count_row = cursor.fetchone()
    author_count = count_row[0] if count_row else 0
    
    if author_count == 0:
        seed_library_data(conn)
        
    conn.commit()
    conn.close()


def seed_library_data(conn):
    """Seed initial 4 real authors and 8 real books into database."""
    cursor = conn.cursor()
    
    authors = [
        (1, 'George Orwell', 'United Kingdom', 'static/uploads/authors/george_orwell.jpg'),
        (2, 'Jane Austen', 'United Kingdom', 'static/uploads/authors/jane_austen.jpg'),
        (3, 'Arthur Conan Doyle', 'United Kingdom', 'static/uploads/authors/arthur_conan_doyle.jpg'),
        (4, 'Naguib Mahfouz', 'Egypt', 'static/uploads/authors/naguib_mahfouz.jpg')
    ]
    
    for a in authors:
        cursor.execute(
            "INSERT OR IGNORE INTO author (author_id, name, country, photo_path) VALUES (?, ?, ?, ?)",
            a
        )
        
    books = [
        (1, 'Nineteen Eighty-Four', 15.99, 1, 'static/uploads/books/1984.jpg'),
        (2, 'Animal Farm', 10.50, 1, 'static/uploads/books/animal_farm.jpg'),
        (3, 'Pride and Prejudice', 12.99, 2, 'static/uploads/books/pride_and_prejudice.jpg'),
        (4, 'Sense and Sensibility', 11.50, 2, 'static/uploads/books/sense_and_sensibility.jpg'),
        (5, 'A Study in Scarlet', 9.99, 3, 'static/uploads/books/a_study_in_scarlet.jpg'),
        (6, 'The Sign of the Four', 10.25, 3, 'static/uploads/books/sign_of_the_four.jpg'),
        (7, 'Palace Walk', 14.50, 4, 'static/uploads/books/palace_walk.jpg'),
        (8, 'The Thief and the Dogs', 12.00, 4, 'static/uploads/books/thief_and_dogs.jpg')
    ]
    
    for b in books:
        cursor.execute(
            "INSERT OR IGNORE INTO book (book_id, title, price, author_id, cover_path) VALUES (?, ?, ?, ?, ?)",
            b
        )
    conn.commit()
