import os
import sqlite3
from threading import Thread

from flask import Flask


def create_app() -> object:
    thread_running = False

    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')

    from .core.routes import blueprint as core_bp
    from .discord.test import run_bot

    app.register_blueprint(core_bp)

    if not thread_running:
        run_bot()
        thread_running = True

    setup()

    return app

def setup() -> None:
    if not os.path.exists('database.db'):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        cursor.execute(
            'CREATE TABLE IF NOT EXISTS user('
            'id TEXT, ' 
            'email TEXT, '
            'student BOOLEAN, '
            'PRIMARY KEY(id, email))'
        )

        cursor.execute(
            'CREATE TABLE IF NOT EXISTS pending_users('
            'id TEXT, '
            'uuid TEXT, '
            'PRIMARY KEY(id)'
            ')'
        )
        connection.close()
