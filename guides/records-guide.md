# Records: SQL for Humans™ – Onboarding Guide

Welcome to the team! 👋 We're excited to have you on board. This guide will help you get up to speed with the **Records** project.

## What This Project Does

Records is a lightweight Python library that makes it dead simple to write and execute raw SQL queries against relational databases. Think of it as the "Goldilocks" of database libraries—not too minimal, not too heavy. Just write your SQL and get back clean, easy-to-work-with results.

The library handles all the boilerplate for you: connection management, result parsing, and data export. Whether you need to query Postgres, MySQL, SQLite, Oracle, RedShift, or MS-SQL, Records gives you a unified, elegant interface.

**Why it matters:** Developers often overthink database interactions. This library lets you focus on what you're actually good at—writing SQL—without fighting ORMs or complex abstractions.

## Tech Stack

- **Language:** Python 3.6+
- **Core Dependencies:**
  - **SQLAlchemy 2+** — Powers all database interactions (connection pooling, query execution, dialect support)
  - **Tablib** — Handles data export to multiple formats (CSV, XLS, JSON, HTML, YAML, Pandas DataFrames)
- **Testing:** tox and pytest (inferred from `.travis.yml`)
- **Supported Databases:** PostgreSQL, MySQL, SQLite, Oracle, RedShift, MS-SQL

Note: Python 2.7 and 3.4/3.5 support was dropped in v0.6.0 when SQLAlchemy 2+ became the requirement. Keep this in mind if you see legacy code around.

## Project Structure

```
records/
├── records/                    # Main package code
│   ├── __init__.py            # Core Database and Record classes
│   └── ...                    # Other modules (structure not fully visible)
├── tests/                     # Unit and integration tests
├── .travis.yml                # CI/CD configuration
├── .gitignore                 # Git ignore rules
├── HISTORY.rst                # Changelog and version history
├── README.rst                 # User-facing documentation
├── MANIFEST.in                # Package manifest for distribution
├── setup.py (implied)         # Package configuration and dependencies
└── requirements.txt           # Python dependencies
```

**Key files to know:**
- **`records/__init__.py`** — This is where the magic happens. Contains `Database`, `Record`, and `RecordCollection` classes.
- **`HISTORY.rst`** — Track version changes here; currently at v0.6.0 (April 2024).
- **`.travis.yml`** — Our CI pipeline tests against Python 3.6+.

## How To Get Started

### 1. Clone and Setup

```bash
git clone https://github.com/psf/records.git
cd records
```

### 2. Install Dependencies

```bash
# Using pip (recommended)
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"  # if a dev extras_require exists
```

### 3. Set Up Your Database Connection

Records supports the `$DATABASE_URL` environment variable for convenience:

```bash
export DATABASE_URL="postgres://user:password@localhost:5432/mydb"
```

Or pass it directly in code:

```python
import records

db = records.Database('postgres://user:password@localhost:5432/mydb')
```

### 4. Write Your First Query

```python
import records

db = records.Database('sqlite:///test.db')
rows = db.query('SELECT * FROM users')

# Access results
print(rows[0])           # First row
print(rows[0].name)      # Access by attribute
print(rows[0]['email'])  # Or by key
print(rows.first())      # Get just the first row

# Export to different formats
print(rows.export('csv'))
```

### 5. Run Tests

```bash
# Using tox (tests multiple Python versions)
tox

# Or pytest directly (faster for development)
pytest tests/
```

## Key Concepts

### The Database Class

Your entry point. Manages connections and query execution:

```python
db = records.Database('postgres://...')
rows = db.query('SELECT * FROM users WHERE active = :active', active=True)
```

**Key methods:**
- `query(sql, **params)` — Execute a query, get back a `RecordCollection`
- `query_file(filename, **params)` — Load SQL from a file and execute
- `bulk_query(sql, dataset)` — Execute the same query multiple times with different parameters
- `transaction()` — Start a transaction for multi-statement operations
- `get_table_names()` — Introspect database schema

### The Record Class

Represents a single row. It's like a dictionary with superpowers:

```python
record = rows[0]

# All these work:
record.username
record['username']
record[0]  # Column index

# Even works with weird column names:
record['user email']  # Spaces are fine!
```

### The RecordCollection Class

A list-like collection of `Record` objects that are cached as you iterate:

```python
rows = db.query('SELECT * FROM users')

# Iteration caches results
for row in rows:
    print(row.name)

# Later access is instant (from cache)
print(rows[0])

# Export to various formats
rows.as_dict()
rows.all()  # Get all rows as a list
rows.first()  # Get first row, or None
rows.export('csv')  # Export to CSV string
rows.dataset  # Tablib Dataset object
```

### Safe Parameterization

Always use parameterized queries to prevent SQL injection:

```python
# ✅ Good
db.query('SELECT * FROM users WHERE id = :id', id=42)

# ❌ Bad (never do this!)
db.query(f'SELECT * FROM users WHERE id = {user_id}')
```

### Transactions

For multi-statement operations:

```python
t = db.transaction()
try:
    db.query('UPDATE users SET active = true WHERE id = :id', id=1)
    db.query('INSERT INTO audit_log VALUES (...)')
    t.commit()
except Exception:
    t.rollback()
```

## Things To Watch Out For

### 1. **Python Version Support**
As of v0.6.0, we only support Python 3.6+. If you find old Python 2.7 code, it's likely dead code. Keep it removed.

### 2. **SQLAlchemy 2.0 Migration**
We recently upgraded to SQLAlchemy 2+, which has breaking changes from 1.x. If you're adding database logic, make sure you're using SQLAlchemy 2+ syntax. Check the [SQLAlchemy 2.0 migration guide](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html) if you hit issues.

### 3. **Result Caching**
Rows are cached as you iterate. This is great for performance but means memory usage grows with result size. For huge datasets, consider pagination or streaming.

```python
rows = db.query('SELECT * FROM massive_table')
for row in rows:  # ← Each row is cached here
    process(row)
```

### 4. **Connection Pooling**
SQLAlchemy handles connection pooling automatically, but be aware that connections are reused. If you're writing integration tests, you might need to clean up between tests.

### 5. **Database Driver Installation**
Records doesn't include database drivers—you need to install them separately:

```bash
pip install psycopg2-binary    # PostgreSQL
pip install mysql-connector-python  # MySQL
pip install pyodbc             # MS-SQL
pip install cx_Oracle          # Oracle
```

### 6. **The `.export()` Method Depends on Tablib**
Exporting requires Tablib to be installed. It should be a dependency, but if you hit import errors, install it explicitly:

```bash
pip install tablib[pandas]
```

### 7. **Column Name Edge Cases**
Non-alphanumeric column names are supported, but stick with snake_case in practice. If you encounter a column with spaces or special characters, use bracket notation:

```python
record['column with spaces']  # ✅ Works
record.column_with_spaces    # ✅ Better
```

---

## Next Steps

1. **Read the README**