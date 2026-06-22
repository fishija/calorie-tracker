from flask import Flask
from config import config
import os

def create_app():
    app = Flask(__name__)
    
    env = os.environ.get("FLASK_ENV", "development")
    app.config.from_object(config[env])

    from app.routes import main
    app.register_blueprint(main)

    return app
