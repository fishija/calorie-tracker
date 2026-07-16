"""Configuration settings for the Flask application.

Loads environment variables from a .env file and defines configurations
for different deployment environments (development, testing, production).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _build_postgres_uri(db_name):
    """Build a Postgres connection string from POSTGRES_* env vars for the given database name."""
    user = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD")
    host = os.environ.get("POSTGRES_HOST", "db")
    return f"postgresql+psycopg://{user}:{password}@{host}/{db_name}"


class Config:
    """Base configuration class containing shared settings and constants."""

    SECRET_KEY = os.environ.get("SECRET_KEY")
    UPLOAD_FOLDER = Path(__file__).parent / "uploads"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
    CLAUDE_MODEL = "claude-sonnet-5"


class DevelopmentConfig(Config):
    """Development configuration class with settings for local development."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or _build_postgres_uri(
        os.environ.get("POSTGRES_DB")
    )


class ProductionConfig(Config):
    """Production configuration class with settings for deployment."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or _build_postgres_uri(
        os.environ.get("POSTGRES_DB")
    )


class TestingConfig(Config):
    """Testing configuration class with settings for running tests.

    Points at a separate throwaway Postgres database (not the dev database,
    and not in-memory SQLite) so the test suite exercises the same engine
    and SQL dialect as production.
    """

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or _build_postgres_uri(
        os.environ.get("POSTGRES_TEST_DB", "app_test")
    )
    WTF_CSRF_ENABLED = False


# Configuration dictionary mapping environment names to their respective configuration classes.
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
