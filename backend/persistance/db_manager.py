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
    """Context manager for DB session"""
    session = db.session
    try:
        yield session
    except Exception as e:
        session.rollback()
        print(f"✗ Database error: {e}")
        raise
    finally:
        session.close()
