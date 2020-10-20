from flask import Flask
from threading import Thread

def create_app():
    thread_running = False

    app = Flask(__name__)
    app.config.from_object('config.DevelopmentConfig')

    from .discord.test import run_bot
    from .core.routes import blueprint as core_bp

    app.register_blueprint(core_bp)

    if not thread_running:
        run_bot()
        thread_running = True

    return app