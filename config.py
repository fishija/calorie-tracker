"""Configuration settings for the Flask application.

Loads environment variables from a .env file and defines configurations
for different deployment environments (development, testing, production).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _get_secret(name, default=None):
    """Retrieve a secret from environment variables or from a file if specified."""
    file_path = os.environ.get(f"{name}_FILE")
    if file_path:
        return Path(file_path).read_text().strip()
    return os.environ.get(name, default)


def _build_postgres_uri(db_name):
    """Build a Postgres connection string from POSTGRES_* env vars for the given database name."""
    user = _get_secret("POSTGRES_USER")
    password = _get_secret("POSTGRES_PASSWORD")
    host = _get_secret("POSTGRES_HOST", "db")
    return f"postgresql+psycopg://{user}:{password}@{host}/{db_name}"


class Config:
    """Base configuration class containing shared settings and constants."""

    SECRET_KEY = _get_secret("SECRET_KEY")
    UPLOAD_FOLDER = Path(__file__).parent / "uploads"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ANTHROPIC_API_KEY = _get_secret("ANTHROPIC_API_KEY")
    CLAUDE_MODEL = "claude-sonnet-5"


class DevelopmentConfig(Config):
    """Development configuration class with settings for local development."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = _get_secret("DATABASE_URL") or _build_postgres_uri(
        _get_secret("POSTGRES_DB")
    )


class ProductionConfig(Config):
    """Production configuration class with settings for deployment."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = _get_secret("DATABASE_URL") or _build_postgres_uri(
        _get_secret("POSTGRES_DB")
    )


class TestingConfig(Config):
    """Testing configuration class with settings for running tests.

    Points at a separate throwaway Postgres database (not the dev database,
    and not in-memory SQLite) so the test suite exercises the same engine
    and SQL dialect as production.
    """

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = _get_secret("TEST_DATABASE_URL") or _build_postgres_uri(
        _get_secret("POSTGRES_TEST_DB", "app_test")
    )
    WTF_CSRF_ENABLED = False


# Configuration dictionary mapping environment names to their respective configuration classes.
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
