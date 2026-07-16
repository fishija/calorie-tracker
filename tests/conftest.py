"""Shared pytest fixtures."""

from urllib.parse import urlsplit

import psycopg
import pytest
from psycopg import sql

from app import create_app
from app.db import db as _db
from app.models import User


def _admin_connection_params(db_uri):
    """Connection info for the Postgres server itself (not a specific
    database), needed to run CREATE DATABASE / DROP DATABASE.

    Derived from the app's actual resolved SQLALCHEMY_DATABASE_URI rather
    than re-reading POSTGRES_* env vars directly, so this can never drift
    from what TestingConfig is really pointed at (e.g. if TEST_DATABASE_URL
    is set instead of POSTGRES_TEST_DB).
    """
    parsed = urlsplit(db_uri)
    return {
        "user": parsed.username,
        "password": parsed.password,
        "host": parsed.hostname or "db",
        "port": parsed.port or 5432,
        "dbname": "postgres",  # maintenance database, always present
    }


def _test_db_name(db_uri):
    return urlsplit(db_uri).path.lstrip("/")


@pytest.fixture(scope="session", autouse=True)
def _test_database():
    """Drop (if present) and recreate the test database before the session,
    then drop it again after.

    Always drop-then-create (rather than create-if-missing) so a database
    left behind by a previous crashed/interrupted run can never leak stale
    tables or rows into this run.
    """
    # Build a throwaway app instance purely to resolve the real config -
    # not used for requests, just to read SQLALCHEMY_DATABASE_URI.
    db_uri = create_app("testing").config["SQLALCHEMY_DATABASE_URI"]
    db_name = _test_db_name(db_uri)
    admin_params = _admin_connection_params(db_uri)

    conn = psycopg.connect(**admin_params, autocommit=True)
    try:
        conn.execute(
            sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(db_name))
        )
        conn.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
    finally:
        conn.close()

    yield

    conn = psycopg.connect(**admin_params, autocommit=True)
    try:
        conn.execute(
            sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(db_name))
        )
    finally:
        conn.close()


@pytest.fixture
def app():
    app = create_app("testing")

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()
        _db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def make_user(db):
    def _make_user(email="test@example.com", username="testuser", password="password123"):
        user = User(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    return _make_user
