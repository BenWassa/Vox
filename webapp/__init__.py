from flask import Flask, render_template
from .config import DevConfig
from .database import DatabaseManager
from .routes import api
import logging


def create_app(config_object=DevConfig):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_object)

    logging.basicConfig(level=app.config['LOG_LEVEL'])
    app.logger.setLevel(app.config['LOG_LEVEL'])

    db = DatabaseManager(app.config['DATA_DIR'])
    api.api_db = db
    app.register_blueprint(api.api_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

