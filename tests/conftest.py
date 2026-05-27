import pytest
from flask import Flask
from backend.persistance.db_manager import db as _db


@pytest.fixture(scope="session")
def app():
    """App configured for testing: in-memory SQLite, no scheduler, no DB seeding."""
    flask_app = Flask(__name__, instance_relative_config=False)
    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        TELEGRAM_BOT_TOKEN="test-token",
        TELEGRAM_CHAT_ID="test-chat",
        APP_TIMEZONE="Etc/GMT+6",
    )

    _db.init_app(flask_app)

    from backend.routes.general import general_blueprint
    from backend.routes.prices import price_blueprint
    from backend.routes.watchlists import watchlist_blueprint
    from backend.routes.alerts import alerts_blueprint

    flask_app.register_blueprint(general_blueprint)
    flask_app.register_blueprint(price_blueprint)
    flask_app.register_blueprint(watchlist_blueprint)
    flask_app.register_blueprint(alerts_blueprint)

    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    """Fresh, empty DB tables for each test."""
    with app.app_context():
        yield _db
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()
