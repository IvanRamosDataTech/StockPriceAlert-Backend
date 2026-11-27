from flask_sqlalchemy import SQLAlchemy
from contextlib import contextmanager

db = SQLAlchemy()

# Columns added after the first release. create_all() never alters existing tables,
# so these are added with ALTER TABLE when missing: (table, column, SQL type).
_ADDED_COLUMNS = [
    ("alert", "last_triggered_price", "FLOAT"),
]

# Lightweight migration is fine for this PoC. WE dont' want touse an specilized migration tool at the moment.
# This approach simply checks for missing columns and adds them if necessary.
def ensure_columns():
    """Idempotently add columns that are missing from existing tables."""
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    for table, column, sql_type in _ADDED_COLUMNS:
        existing = {col["name"] for col in inspector.get_columns(table)}
        if column not in existing:
            with db.engine.begin() as conn:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}"))
            print(f"✓ Added column {table}.{column}")

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    with app.app_context():
        from .db_utils import is_db_empty, populate_database
        db.create_all()
        ensure_columns()
        if is_db_empty():
            print("Seeding default data...")
            populate_database()
        print("✓ Database initialized")

@contextmanager
def get_db_session():
    """
    Context manager that provides a database session for use in a with-statement.

    Usage:
        with get_db_session() as session:
            # use session here

    Behavior:
    - On entry, the function obtains the configured DB session and then yields it to the caller.
    - The line `yield session` hands the session object to the code inside the `with` block and suspends this generator-based context manager.
    - When the `with` block finishes (normally or via exception), execution resumes immediately after the `yield`.
    - If an exception occurred inside the `with` block, that exception is propagated back into this generator at the yield point, triggering the `except` block: the session is rolled back, an error is logged/printed, and the exception is re-raised.
    - The `finally` block always runs afterwards to close the session and release resources.

    Returns:
        The active database session for use within the `with` block.
    """
    session = db.session
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"✗ Database error: {e}")
        raise
    finally:
        session.close()
