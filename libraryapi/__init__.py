import logging
import time

from flasgger import Swagger
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .config import Config, TestConfig

db = SQLAlchemy()

SERIAL_NUMBER_DIGITS = 6


def create_app(test=False):
    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)
    swagger = Swagger(app, template={
        "info": {
            "title": "Library API",
            "description": "API for a simple library",
            "version": "1.0.0"
        },
        "host": "localhost:8000",
        "basePath": "/api",
        "schemes": ["http"],
    })
    if test:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        from .routes import books_bp, users_bp
        app.register_blueprint(books_bp, url_prefix='/api/books')
        app.register_blueprint(users_bp, url_prefix='/api/users')

        tries = 10
        attempt = 1
        interval = 2
        app.logger.info("Creating the database...")
        while attempt < tries:
            try:
                db.create_all()
            except Exception as ex:
                attempt += 1
                app.logger.warning(f"Failed to create db, attempt {attempt}/{tries} in {interval}s")
                if attempt > tries:
                    raise ex
                time.sleep(interval)
            else:
                app.logger.info("Created the database successfully!")
                break
    return app
