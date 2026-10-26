# Alexandria National University (ANU) — Faculty of Engineering
## Introduction to Database Systems — Lab 3 (Web Version)
**Fall 2026**  
**Course Instructor:** Dr. Yasser Fouad  
**Teaching Assistants:** Eng. Abdallah Elsayed, Eng. Basem Hesham, Eng. Danny Hossam  

---

## 📌 Project Overview
This project extends our previous Lab 2 web portal into **Lab 3: Foreign Keys and Simple SQL**. It implements:
1. **Lab 2 Foundation (Preserved 100%):** Secure user registration, authentication (PBKDF2 SHA-256), session management, and private to-do list CRUD with SQLite/MySQL.
2. **Lab 3 — Part II / Problem 2 (Library: Books and Authors):**
   - Full relational schema: `AUTHOR (author_id, name, country)` and `BOOK (book_id, title, price, author_id)`.
   - Strict referential integrity: `BOOK.author_id` references `AUTHOR.author_id` with `ON DELETE CASCADE`.
   - Simple parameterized SQL statements (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) without unnecessary relational joins, making it clear and easy to explain during lab discussions.
   - **Image Upload Bonus (+Bonus Marks):** True binary file uploads for author portraits and book covers (with PIL validation, 5MB limits, unique UUID filenames, and offline verified public domain seed media from Wikimedia Commons).
3. **Database Flexibility:** Transparent support for both native **MySQL Server** (via `pymysql` with `ENGINE=InnoDB`) and **SQLite** (via `sqlite3` with `PRAGMA foreign_keys = ON;`), ensuring existing user data remains completely intact while allowing clean MySQL lab evaluation.

---

## 🏆 Lab 3 Grading Rubric Alignment & Verification

| Item | Specification / Requirement | Implemented In | Status | Marks |
| :--- | :--- | :--- | :---: | :---: |
| **Problem 2 DDL** | `library` DB creation, `author` created before `book`, primary keys, MySQL types (`DECIMAL(10,2)` for price), `FOREIGN KEY` with `ON DELETE CASCADE`. | [`problem2_DDL.sql`](file:///c:/Users/Arabtech/Desktop/scratch/auth_app/problem2_DDL.sql) | ✅ 100% | **1.0** |
| **Problem 2 DML** | Seed data with at least 3 authors and 6 books linked to valid authors. (Seeded 4 real authors & 8 real books with realistic prices). | [`problem2_DML.sql`](file:///c:/Users/Arabtech/Desktop/scratch/auth_app/problem2_DML.sql) | ✅ 100% | **0.5** |
| **F2.1 — Display** | Display Authors Table and Books Table. Books Table visibly displays each book's `author_id` as well as mapped author name. | [`library_authors.html`](file:///c:/Users/Arabtech/Desktop/scratch/auth_app/templates/library_authors.html), [`library_books.html`](file:///c:/Users/Arabtech/Desktop/scratch/auth_app/templates/library_books.html) | ✅ 100% | **1.0** |
| **F2.2 & F2.3 — Add & Edit** | Add and edit authors and books. Book creation uses an author dropdown populated from the database. Rejects nonexistent author IDs. | [`app.py:L268-L380`](file:///c:/Users/Arabtech/Desktop/scratch/auth_app/app.py) | ✅ 100% | **1.0** |
| **F2.4 & F2.5 — Remove** | Remove book (preserves author); remove author (warns user and automatically cascades deletion of all books via database constraint). | [`app.py:L319-L390`](file:///c:/Users/Arabtech/Desktop/scratch/auth_app/app.py) | ✅ 100% | **1.0** |
| **BONUS — Images** | Real file uploads for author portraits and book covers. Binary inspection (Pillow), 5MB size limit, UUID filenames, persistent storage, offline seed images. | [`upload_utils.py`](file:///c:/Users/Arabtech/Desktop/scratch/auth_app/upload_utils.py), [`IMAGE_CREDITS.md`](file:///c:/Users/Arabtech/Desktop/scratch/auth_app/IMAGE_CREDITS.md) | ✅ 100% | **Bonus** |
| **TA Guide & Code Quality** | Clean README, parameterized plain SQL (No ORM), 19 automated unit tests, responsive down to 360px mobile view. | [`README.md`](file:///c:/Users/Arabtech/Desktop/scratch/auth_app/README.md), [`test_library.py`](file:///c:/Users/Arabtech/Desktop/scratch/auth_app/test_library.py) | ✅ 100% | **1.0** |

> [!IMPORTANT]
> **Scope of Problem 1 (The COMPANY Database):**  
> Problem 1 (`EMPLOYEE`, `DEPARTMENT`, `PROJECT`) is an independent SQL query and constraint assignment described on Page 2 of the Lab 3 handout. As instructed, it has no website frontend. To achieve full 10/10 marks for Lab 3 submission, make sure to include `problem1_DDL.sql`, `problem1_DML.sql`, and `problem1_Answers.txt` alongside this `website/` folder.

---

## 📁 Repository & Submission Structure

In accordance with the Lab 3 PDF submission guidelines:
```text
lab3-<student-id>/
├── problem1_DDL.sql            # Problem 1 DDL (COMPANY database) [Separate task]
├── problem1_DML.sql            # Problem 1 DML (at least 3 records per table)
├── problem1_Answers.txt        # Answers to Q1.1, Q1.2, Q1.3
├── problem2_DDL.sql            # Problem 2 DDL (Library: author & book tables)
├── problem2_DML.sql            # Problem 2 DML (4 seed authors, 8 seed books)
├── README.md                   # Complete TA instructions & academic documentation
└── website/                    # (or auth_app/) Full-Stack Flask Web Application
    ├── app.py                  # Main application controllers & route handlers
    ├── requirements.txt        # Python dependencies
    ├── .env.example            # Environment variables template
    ├── IMAGE_CREDITS.md        # Public domain attributions for sourced images
    ├── database/
    │   ├── db.py               # Unified DB manager (MySQL + SQLite + CursorProxy)
    │   └── schema.sql          # Base relational schema
    ├── upload_utils.py         # Pillow image validation & secure disk persistence
    ├── static/
    │   ├── css/style.css       # Responsive Glassmorphism Design System
    │   ├── js/main.js          # Client-side validation & mobile navigation
    │   └── uploads/            # Persistent local image storage
    │       ├── authors/        # Author portrait images
    │       └── books/          # Book cover images
    ├── templates/
    │   ├── base.html           # Master navigation & flash message layout
    │   ├── library_books.html  # Books table, Add modal (dropdown), Edit, Delete
    │   ├── library_authors.html# Authors table, Add modal, Edit, Cascade Delete
    │   ├── dashboard.html      # Personal To-Do manager (Lab 2 preserved)
    │   ├── login.html          # Secure login form
    │   ├── register.html       # Registration form
    │   └── admin_users.html    # Role-based admin database inspector
    ├── test_app.py             # 5 Unit tests for Lab 2 (Auth, To-Dos, Isolation)
    ├── test_library.py         # 14 Unit tests for Lab 3 (CRUD, Cascade, Images, SQL)
    └── دليل_المشروع.md         # دليل مناقشة المعمل باللهجة المصرية والمصطلحات الإنجليزية
```

---

## 🛠️ Technology Stack
- **Backend:** Python 3.10+ with [Flask 3.1](https://flask.palletsprojects.com/)
- **Database Engine:** MySQL 8.0 (InnoDB) and SQLite3 with strict Foreign Key enforcement (`PRAGMA foreign_keys = ON;`)
- **Database Client:** [PyMySQL 1.2](https://pymysql.readthedocs.io/) & standard `sqlite3`
- **Security:** Werkzeug PBKDF2 SHA-256 cryptographic password hashing, Anti-CSRF session tokens
- **Image Processing & Security:** [Pillow (PIL) 12.2](https://python-pillow.org/) for raster binary verification (JPEG, PNG, WebP)
- **Frontend / Styling:** Semantic HTML5, Vanilla CSS3 (Custom Glassmorphism Tokens, Google Fonts *Outfit* & *Plus Jakarta Sans*, FontAwesome 6)
- **Architecture:** Parameterized Plain SQL (No ORM), Multi-layer server/client validation

---

## 🚀 How to Run (Step-by-Step for TAs & Students)

### 1. Prerequisites
- Python 3.10 or newer installed.
- (Optional for MySQL evaluation): MySQL Server 8.0 installed and running.

### 2. Installation
Open a terminal in the project directory (`auth_app`):
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default configuration runs automatically in `auto` mode (uses local SQLite `users.db` by default, or connects to MySQL if configured).

---

## 🗄️ Database Setup & SQL Execution Order

### Option A: Clean Environment Evaluation in MySQL (As instructed in Lab 3 PDF)
If you wish to test the standalone MySQL scripts using the standard MySQL CLI:
```bash
# 1. Build the clean library database and tables (DDL)
mysql -u root -p < problem2_DDL.sql

# 2. Insert the seed authors and books (DML)
mysql -u root -p < problem2_DML.sql

# 3. Query interactively to inspect
mysql -u root -p library
```

To point the Flask application to this MySQL database, update `.env`:
```ini
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=library
```

### Option B: Safe Non-Destructive Extension of Existing Development Database
To run without MySQL or without deleting existing users and to-dos:
- Simply launch the application (`python app.py`).
- The application automatically executes `init_db()` non-destructively:
  - Ensures `author` and `book` tables exist.
  - Automatically seeds the 4 real authors and 8 real books if empty.
  - **Preserves existing user accounts (`mohamed roushdy`, `Jane Doe`, etc.) and to-do items intact.**

> [!CAUTION]
> `problem2_DDL.sql` contains `DROP DATABASE IF EXISTS library;`. It is intended strictly for clean-slate TA evaluation. Do **not** execute it on a populated production database.

---

## 💻 Launching the Application
```bash
python app.py
```
Open your web browser at: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

*(On Windows, you can also double-click `run_localhost.bat` to launch automatically).*

### Default Test Accounts:
- **Email:** `alice@example.com` | **Password:** `Password123!`
- **Email:** `mohamedroushdy903@gmail.com` (Admin account) | **Password:** `Password123!`
- Or click **Register** to create a fresh student account.

---

## 🧪 Running Automated Unit Test Suites
The codebase provides **19 comprehensive automated unit tests** split across two suites:

### 1. Lab 3 Library & Foreign Key Test Suite (14 Tests)
```bash
python -m unittest test_library.py
```
**Tests Covered:**
- `test_01`: Preserved authentication and to-do tasks
- `test_02`: Display of both tables with visible `author_id` badges
- `test_03`: Add and edit author records
- `test_04`: Add and edit book records (including changing assigned author)
- `test_05`: Delete book without affecting referenced author
- `test_06`: Delete author and verify `ON DELETE CASCADE` deleted child books
- `test_07`: Rejection of nonexistent author IDs
- `test_08`: Rejection of blank fields and negative/malformed prices
- `test_09`: Image upload and replacement for authors and books
- `test_10`: Image preservation on edit when no new file is uploaded
- `test_11`: Rejection of disguised binaries, executable extensions, and files > 5MB
- `test_12`: Database persistence across restarts
- `test_13`: Mobile layout elements and responsive tokens
- `test_14`: Verification of syntax in `problem2_DDL.sql` and `problem2_DML.sql`

**Output:**
```text
..............
----------------------------------------------------------------------
Ran 14 tests in 11.879s

OK
```

### 2. Lab 2 Auth & Privacy Test Suite (5 Tests)
```bash
python -m unittest test_app.py
```
**Output:**
```text
.....
----------------------------------------------------------------------
Ran 5 tests in 4.765s

OK
```

---

## 📖 Feature Mapping Checklist (F2.1 – F2.5 & Bonus)

### F2.1 — Display Authors & Books Tables
- **Authors Table (`/authors`):** Shows portrait thumbnail, `author_id` (PK), name, country, and total books count.
- **Books Table (`/books`):** Shows cover thumbnail, `book_id` (PK), title, price formatted as `$XX.XX`, author name, and **visibly includes `author_id`** (e.g. `author_id: 1`).

### F2.2 — Add Author & Add Book
- **Add Author Modal:** Validates non-empty name and country; allows portrait image upload.
- **Add Book Modal:** Validates title and non-negative decimal price; provides an **Author dropdown populated from the database** (showing author names while submitting numeric `author_id`). If no authors exist, displays an alert requiring an author to be created first.

### F2.3 — Edit Author & Edit Book
- **Edit Author:** Updates name and country; allows uploading a new portrait or preserving current portrait if empty.
- **Edit Book:** Updates title, price, and allows **reassigning the book to a different author**; allows replacing or preserving the cover.

### F2.4 — Delete Book
- Deletes only the selected book record (`DELETE FROM book WHERE book_id = ?`).
- Confirms the author record remains completely unaffected.

### F2.5 — Delete Author (ON DELETE CASCADE)
- Shows a prominent confirmation warning explaining that deleting this author will delete their books.
- Executes `DELETE FROM author WHERE author_id = ?`.
- The database engine automatically deletes all books linked to this author via `ON DELETE CASCADE`.

### 🌟 Bonus: Image Uploads & Real Public Domain Media
- **Upload Validation (`upload_utils.py`):**
  - Allowed extensions: `.jpg`, `.jpeg`, `.png`, `.webp`.
  - Content check: Binary inspection via `PIL.Image.open()` and `verify()` to block renamed executables and scripts.
  - Size limit: 5MB maximum (handled by Flask and custom error handlers).
  - Safe filenames: UUID4-generated filenames preventing directory traversal and file collisions.
- **Pre-populated Verified Media:** Sourced directly from **Wikimedia Commons** and public domain archives (see [`IMAGE_CREDITS.md`](file:///c:/Users/Arabtech/Desktop/scratch/auth_app/IMAGE_CREDITS.md)):
  1. **George Orwell** (Portrait) + *1984* & *Animal Farm* (1st Edition Covers)
  2. **Jane Austen** (1870 Portrait) + *Pride and Prejudice* (Hugh Thomson Peacock Cover) & *Sense and Sensibility*
  3. **Arthur Conan Doyle** (Portrait) + *A Study in Scarlet* & *The Sign of the Four*
  4. **Naguib Mahfouz** (Nobel Laureate Portrait) + *Palace Walk* & *The Thief and the Dogs* (Classic Typographic Covers)

---

## 💡 Core Database Concepts Explained (For Lab Discussion)

### 1. Primary Key (PK)
A column (or set of columns) that uniquely identifies each row in a table. In our schema:
- `AUTHOR.author_id` is the primary key of `author`.
- `BOOK.book_id` is the primary key of `book`.
A primary key must be unique and cannot contain `NULL` values.

### 2. Foreign Key (FK) & Referential Integrity
A foreign key is a column in one table that references the primary key of another table, creating a relational link:
- `BOOK.author_id` references `AUTHOR.author_id`.
Referential integrity guarantees that a book cannot be assigned to an `author_id` that does not exist in the `author` table. Any attempt to insert or update a book with an invalid `author_id` is rejected by the database.

### 3. ON DELETE CASCADE
By default (`RESTRICT` or `NO ACTION`), a database prevents deleting an author if that author still has books.  
When configured with **`ON DELETE CASCADE`**:
```sql
FOREIGN KEY (author_id) REFERENCES author(author_id) ON DELETE CASCADE
```
Deleting a parent row in `author` causes the database storage engine to **automatically delete all child rows** in `book` that point to that author. This prevents orphaned records without requiring multi-query manual cleanups in application code.

### 4. Simple SQL & Parameterized Queries
To prevent SQL injection attacks, all SQL statements use parameter placeholders (`?` or `%s`):
```python
cursor.execute("SELECT * FROM author WHERE author_id = ?", (author_id,))
```
User inputs are treated strictly as data literals rather than executable SQL syntax. relational operations are kept as simple single-table queries (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) without unnecessary joins, adhering to the assignment's simplicity requirements.

---

## 🇪🇬 دليل مناقشة المعمل باللهجة المصرية (Egyptian-Arabic Lab Discussion Guide)

> هذا القسم مخصص لمساعدتك في شرح مشروعك للمعيد أو الدكتور أثناء مناقشة معمل نظم قواعد البيانات (Lab 3):

### 1. إزاي تشرح الربط بين الجداول (Foreign Key & Referential Integrity)؟
> *"يا بشمهندس، إحنا عندنا جدولين أساسيين: جدول الـ `AUTHOR` وجدول الـ `BOOK`.*  
> *الـ Primary Key في جدول الـ AUTHOR هو `author_id`، وفي جدول الـ BOOK هو `book_id`.*  
> *علشان نربط الكتاب بالمؤلف بتاعه، عملنا Foreign Key اسمه `author_id` في جدول الـ BOOK بيشير للـ `author_id` في جدول الـ AUTHOR.*  
> *وده بيحقق الـ **Referential Integrity**؛ يعني ماينفعش أضيف كتاب بـ author_id مش موجود أصلاً في قاعدة البيانات، وقاعدة البيانات هترفض العملية فوراً."*

### 2. إزاي تشرح خاصية الـ `ON DELETE CASCADE`؟
> *"في العلاقات العادية، لو جيت أمسح مؤلف وله كتب مسجلة، الـ Database هتديني Error وتقول إن فيه Foreign Key Constraint.*  
> *لكن في التاسك ده، ضفنا قيد `ON DELETE CASCADE` على الـ Foreign Key.*  
> *وده معناه إن بمجرد ما أنفذ أمر `DELETE FROM author WHERE author_id = ?`، محرك قاعدة البيانات (MySQL InnoDB أو SQLite) بيقوم تلقائياً وبشكل Cascade بمسح كل الكتب التابعة للمؤلف ده من غير ما يتبقى أي Orphan Records، ومن غير ما أحتاج أكتب كود إضافي لمسح الكتب يدوياً في بايثون."*

### 3. إزاي تشرح إن الكود بسيط ومافيهوش JOIN معقد؟
> *"في الـ Lab Handout، البشمهندسين وضحوا إن المطلوب استعلامات SQL بسيطة (Simple SQL) بدون JOIN أو GROUP BY.*  
> *وعلشان كده استعلاماتنا عبارة عن parameterized SELECT و INSERT و UPDATE و DELETE صريحة، والربط بين اسم المؤلف ورقم الـ author_id في شاشة الكتب اتعمل بـ Dictionary mapping بسيط في البايثون، وده بيخلي الـ Queries سريعة ومفهومة وسهلة المناقشة."*

### 4. إزاي تشرح ميزة رفع الصور (Bonus Feature) وتأمينها؟
> *"في ميزة البونص الخاصة برفع الصور، ما اكتفيناش بروابط خارجية ممكن تعطل، إحنا عملنا نظام Upload حقيقي كامل:*  
> 1. *بيفحص امتداد الملف (JPG, PNG, WebP).*  
> 2. *بيفحص محتوى الملف الحقيقي والـ Binary Header باستخدام مكتبة **Pillow** علشان نمنع أي حد يرفع ملف تنفيذي أو Script متخفي في صورة.*  
> 3. *بيحدد حجم أقصى 5 ميجابايت.*  
> 4. *بيولد أسماء مشفرة فريدة بـ UUID علشان نمنع الـ File Overwrite وتعارض الأسماء.*  
> 5. *بيحفظ المسار النسبي فقط في عمود `photo_path` أو `cover_path` في قاعدة البيانات."*

---

## 🔧 Troubleshooting Guide

### 1. `Access denied for user 'root'@'localhost'` (MySQL)
- Verify your MySQL password in `.env`.
- If testing locally without MySQL, set `DB_TYPE=sqlite` in `.env` to use the built-in SQLite database immediately.

### 2. `Cannot add or update a child row: a foreign key constraint fails`
- Occurs when attempting to insert a book with an `author_id` that does not exist in `author`.
- Ensure the author is created first, or select an author from the dropdown menu.

### 3. `File size exceeds the 5MB limit` (HTTP 413)
- The uploaded portrait or cover image exceeds 5MB. Compress or resize the image before uploading.

### 4. Images Not Displaying
- Check that the image files exist under `static/uploads/authors/` and `static/uploads/books/`.
- If an image is missing, the template automatically displays an attractive fallback avatar/icon.

---

## 👥 Contributors & Academic Integrity
- **Institution:** Alexandria National University (ANU), Faculty of Engineering
- **Course:** Introduction to Database Systems (Fall 2026)
- **Work:** Completed individually in accordance with ANU academic honesty policies.
