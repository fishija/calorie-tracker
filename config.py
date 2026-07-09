"""Configuration settings for the Flask application.

Loads environment variables from a .env file and defines configurations
for different deployment environments (development, production).
"""

from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()


class Config:
    """Base configuration class containing shared settings and constants."""

    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    UPLOAD_FOLDER = Path(__file__).parent / "uploads"

    # Little fun stuff
    FOOD_ICONS = [
        "🍇","🍈","🍊","🍋","🍌","🍍","🥭","🍎","🍐","🍑","🍒",
        "🍓","🫐","🍅","🫒","🥑","🍆","🥕","🌽","🌶️","🫑","🥒",
        "🥦","🧄","🧅","🥜","🫚","🫛","🍞","🥐","🥨","🧇","🧀",
        "🍗","🥩","🥓","🍔","🍟","🍕","🌭","🥪","🌮","🌯","🫔",
        "🥗","🍿","🥫","🍝","🍱","🍙","🍜","🍣","🍤","🍥","🥮",
        "🥟","🥠","🍦","🍩","🍪","🍰","🧁","🍫","🍬","🍭","🍵",
        "🍾","🍷","🍹","🧋","🧃"
    ]


class DevelopmentConfig(Config):
    """Development configuration class with settings for local development."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration class with settings for deployment."""
    DEBUG = False


# Configuration dictionary mapping environment names to their respective configuration classes.
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
