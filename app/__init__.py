import os
import sqlite3
from threading import Thread

from flask import Flask

from .extensions import database, mail


def create_app() -> object:
    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')

    from .core.routes import blueprint as core_bp
    from .user.routes import blueprint as user_bp
    
    app.register_blueprint(core_bp)
    app.register_blueprint(user_bp)

    register_extensions(app)

    return app


def register_extensions(app: object) -> None:
    mail.init_app(app)
    database.init_app(app)

    from .user.models import User


    with app.app_context():
        engine = database.get_engine()
        table_exists = engine.dialect.has_table(engine, User.__tablename__)

        if not table_exists:
            database.create_all()
            database.session.commit()