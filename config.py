"""Configuration settings for the Flask application.

Loads environment variables from a .env file and defines configurations
for different deployment environments (development, production).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class containing shared settings and constants."""

    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    UPLOAD_FOLDER = Path(__file__).parent / "uploads"

    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
    CLAUDE_MODEL = "claude-sonnet-5"


class DevelopmentConfig(Config):
    """Development configuration class with settings for local development."""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration class with settings for deployment."""

    DEBUG = False


class TestingConfig(Config):
    """Testing configuration class with settings for running tests."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


# Configuration dictionary mapping environment names to their respective configuration classes.
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
