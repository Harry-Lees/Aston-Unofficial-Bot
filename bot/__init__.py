from flask import Flask
from threading import Thread
import os
import sqlite3

def create_app() -> object:
    thread_running = False

    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')

    from .discord.test import run_bot
    from .core.routes import blueprint as core_bp

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

        cursor.execute('CREATE TABLE IF NOT EXISTS verification_keys(email TEXT, verification_code TEXT, expires_on INT)')
        connection.close()