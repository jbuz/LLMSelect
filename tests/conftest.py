import os
import tempfile

import pytest

from llmselect import create_app
from llmselect.extensions import db


@pytest.fixture(scope="session")
def app():
    os.environ.setdefault("FLASK_ENV", "development")
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")
    os.environ.setdefault("ENCRYPTION_KEY", "V9itAn6qCAdzBsZIxwQhO_coouCcjn0H0vCv2UEd8hY=")
    os.environ.setdefault("ALLOW_OPEN_REGISTRATION", "true")
    db_fd, db_path = tempfile.mkstemp(prefix="llmselect-tests-", suffix=".db")
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    application = create_app()
    application.config.update(TESTING=True)

    with application.app_context():
        db.drop_all()
        db.create_all()

    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(autouse=True)
def _reset_database(app):
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
    yield


@pytest.fixture()
def client(app):
    return app.test_client()
