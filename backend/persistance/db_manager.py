from flask_sqlalchemy import SQLAlchemy
from contextlib import contextmanager

db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    with app.app_context():
        from backend.models import asset, alert, watchlist
        db.create_all()
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
