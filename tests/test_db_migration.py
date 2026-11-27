from flask import Flask
from sqlalchemy import inspect, text

from backend.persistance.db_manager import db, ensure_columns


def _columns(engine):
    return {c["name"] for c in inspect(engine).get_columns("alert")}


def test_ensure_columns_adds_missing_column_and_is_idempotent(tmp_path):
    flask_app = Flask(__name__)
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{tmp_path / 'old.db'}"
    db.init_app(flask_app)
    with flask_app.app_context():
        with db.engine.begin() as conn:
            conn.execute(text(
                "CREATE TABLE alert (id INTEGER PRIMARY KEY, ticker VARCHAR NOT NULL, "
                "alert_type VARCHAR(20) NOT NULL, price_threshold FLOAT, last_triggered_at DATETIME)"
            ))
        assert "last_triggered_price" not in _columns(db.engine)

        ensure_columns()
        assert "last_triggered_price" in _columns(db.engine)

        ensure_columns()  # second run is a no-op
        assert "last_triggered_price" in _columns(db.engine)
        db.session.remove()
        db.engine.dispose()
