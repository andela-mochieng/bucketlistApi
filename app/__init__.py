"""This module configures and creates a Flask app instance."""

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()


def make_app(config_name):
    """
    Create a Flask application instance.
    Args:
        config_name (str): A configuration to use for the application.
    Returns:
        app: A Flask application instance with extensions initialized.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    return app

create_app = make_app('development')
