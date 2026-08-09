"""Application factory module for initializing the Flask app."""

import os

import anthropic
from flask import Flask
from flask_login import LoginManager

from app.context_processors import register_context_processors
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

    # create Anthropic client
    app.extensions["anthropic_client"] = anthropic.Anthropic(
        api_key=app.config["ANTHROPIC_API_KEY"]
    )

    init_db(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.auth.routes import auth_bp
    from app.goals.routes import goals_bp
    from app.meals.routes import meals_bp
    from app.routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(meals_bp)

    register_context_processors(app)

    return app
