# Welcome to Records! 🎉

Hey there! Welcome to the team. I'm excited to have you join us on the Records project. This guide will get you up to speed quickly. Don't hesitate to ask questions as you explore the codebase!

## What This Project Does

Records is a lightweight Python library that makes working with SQL databases dead simple. Think of it as a "middle ground" between raw SQL and heavy ORMs like SQLAlchemy.

**The core idea:** You already know SQL, so why should you have to learn some complex framework just to query a database? With Records, you write normal SQL, execute it, and get back results in a Pythonic, easy-to-work-with format.

**Real-world use cases:**
- Running ad-hoc analytics queries and exporting results to CSV/JSON/Excel
- Building data pipelines that need to extract from databases
- Generating reports without the overhead of a full ORM
- One-off scripts that need database access

**Supported databases:** PostgreSQL, MySQL, SQLite, Oracle, RedShift, and MS-SQL.

## Tech Stack

- **Language:** Python 3.6+ (we recently dropped Python 2.7 support)
- **Core dependencies:**
  - **SQLAlchemy 2.x** - The database abstraction layer that handles connections and SQL execution
  - **Tablib** - Handles data export to various formats (CSV, JSON, XLS, YAML, HTML, Pandas DataFrames)
- **Testing:** Tox (run tests against multiple Python versions)
- **CI/CD:** Travis CI

## Project Structure

```
records/
├── records/              # Main package directory
│   ├── __init__.py      # Public API exports
│   ├── core.py          # Database and RecordCollection classes (the heart of the library)
│   ├── models.py        # Record class definition (represents a single row)
│   └── cli.py           # Command-line interface tool
├── tests/               # Test suite
├── setup.py             # Package configuration
├── tox.ini              # Testing configuration
├── .travis.yml          # CI configuration
├── HISTORY.rst          # Changelog
└── README.rst           # User-facing documentation
```

**Key files to understand:**

- **`core.py`** - Contains the `Database` class (handles connections, queries) and `RecordCollection` class (handles result sets). This is where 80% of the logic lives.
- **`models.py`** - The `Record` class, which represents a single row of results. It's a namedtuple-like object that supports dict-style access.
- **`cli.py`** - A command-line tool for exporting query results without writing Python code.

## How To Get Started

### 1. Clone and Install

```bash
git clone https://github.com/psf/records.git
cd records
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"   # Install in development mode with dev dependencies
```

### 2. Verify Installation

```bash
python -c "import records; print(records.__version__)"
```

### 3. Run the Tests

```bash
tox
```

Or test a specific Python version:

```bash
tox -e py39
```

### 4. Try It Out

Create a test script `test_records.py`:

```python
import records

# Connect to a database (SQLite for testing)
db = records.Database('sqlite:///test.db')

# Create a simple table
db.query('CREATE TABLE IF NOT EXISTS users (id INTEGER, name TEXT, email TEXT)')

# Insert some data
db.query('INSERT INTO users VALUES (1, "Alice", "alice@example.com")')
db.query('INSERT INTO users VALUES (2, "Bob", "bob@example.com")')

# Query the data
rows = db.query('SELECT * FROM users')

# Access results
print(rows.first())           # First row as a Record object
print(rows[0].name)           # Access by attribute
print(rows[0]['email'])       # Access by key
for row in rows:              # Iterate
    print(row.name, row.email)
```

Run it:

```bash
python test_records.py
```

## Key Concepts

### The Database Object

```python
db = records.Database('postgres://user:password@localhost/mydb')
```

This is your connection manager. It handles all database interactions and supports:
- `db.query(sql_string)` - Execute a query and get back results
- `db.query_file('path/to/query.sql')` - Execute SQL from a file
- `db.transaction()` - Begin a transaction
- `db.bulk_query()` - Execute multiple queries efficiently
- `db.get_table_names()` - Introspect the database

### The RecordCollection Object

When you call `db.query()`, you get back a `RecordCollection` — basically a list of `Record` objects that are lazy-loaded and cached.

```python
rows = db.query('SELECT * FROM users')  # RecordCollection

rows[0]           # Access by index
rows.first()      # Get first result
rows.all()        # Get all results as a list
rows.as_dict()    # Convert to dict
```

**Important:** Results are cached after access, so iterating twice is efficient — the second time uses the cache.

### The Record Object

Each row is a `Record` — think of it as a smart dict that also acts like a named tuple:

```python
row = rows[0]

# All these work:
row.user_email                # Attribute access
row['user_email']             # Dict-style access
row[3]                        # Index access

# Even works with non-alphanumeric column names:
row['user email']             # Spaces are no problem!
```

### Safe Parameterization

Never use string concatenation for user input! Use SQLAlchemy-style parameters:

```python
# GOOD ✅
rows = db.query('SELECT * FROM users WHERE id = :user_id', user_id=42)

# BAD ❌
rows = db.query(f'SELECT * FROM users WHERE id = {user_id}')
```

### Data Export

This is one of Records' superpowers — convert results to various formats in one line:

```python
rows = db.query('SELECT * FROM active_users')

# Export options:
print(rows.export('csv'))      # Comma-separated values
print(rows.export('json'))     # JSON
print(rows.export('xlsx'))     # Excel
print(rows.export('yaml'))     # YAML
print(rows.dataset.df)         # Pandas DataFrame (via .dataset property)
```

## Things To Watch Out For

### 1. **SQLAlchemy 2.0 Migration (Recent!)**

We recently upgraded to SQLAlchemy 2.x. If you see code using old-style `create_engine()` patterns or if you find yourself confused about connection pooling — that's probably why. The API is mostly the same but some internals changed.

**Watch for:** Old code examples online that reference SQLAlchemy 1.x syntax. Check our HISTORY.rst if you hit version-related issues.

### 2. **Python Version Matters**

We dropped Python 2.7 and 3.4 support in v0.6.0. If someone asks you to support older versions, that's a breaking change and requires careful planning.

### 3. **Lazy Loading is a Feature, Not a Bug**

Results aren't fetched from the database until you access them. This is efficient, but remember:

```python
rows = db.query('SELECT * FROM huge_table')
# ^ No data fetched yet!

first_row = rows[0]
# ^ NOW data is fetched (and cached)
```

If you're working with huge result sets, be mindful of memory usage.

### 4. **Database Connection Strings**

Always use environment variables for production credentials:

```python
import os
db_url = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
db = records.Database(db_url)
```

Never hardcode credentials in the codebase.

### 5. **Transactions Need Explicit Commit**

```python
t = db.transaction()
db.query('INSERT INTO users VALUES (...)')
t.commit()  # Required! Otherwise changes won't persist
```

Forgetting `.commit()` is a common mistake.

### 6. **The CLI Tool is Real**

```bash
records