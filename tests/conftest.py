import pytest

from app import create_app
from models import db


@pytest.fixture
def app(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-only-not-a-secret",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
        }
    )
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        # Close pooled SQLite connections so no ResourceWarning leaks.
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()
