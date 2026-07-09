"""Database module for initializing SQLAlchemy and Flask-Migrate."""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    """Initialize the database with the Flask application.

    Args:
        app (Flask): The Flask application instance.
    """
    db.init_app(app)
    migrate.init_app(app, db)
