from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        from .routes import books_bp
        app.register_blueprint(books_bp, url_prefix='/books')

        db.create_all()

    return app
