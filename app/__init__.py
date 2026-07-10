"""Application factory module for initializing the Flask app."""

import os
import random

from flask import Flask
from flask_login import LoginManager

from app.db import db, init_db
from config import config

login_manager = LoginManager()


def create_app(config_name=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)

    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app.config.from_object(config[config_name])

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    init_db(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.auth.routes import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.routes import main_bp

    app.register_blueprint(main_bp)

    from app.goals.routes import goals_bp

    app.register_blueprint(goals_bp, url_prefix="/goals")

    from app.meals.routes import meals_bp

    app.register_blueprint(meals_bp, url_prefix="/meals")

    @app.context_processor
    def inject_food_icon():
        return dict(current_food_icon=random.choice(app.config["FOOD_ICONS"]))

    return app
