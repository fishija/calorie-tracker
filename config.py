from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()


class Config:
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
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
