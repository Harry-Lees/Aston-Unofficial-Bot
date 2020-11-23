from flask import Flask

from .extensions import database, mail, login_manager, bcrypt, discord


def create_app() -> object:
    app = Flask(__name__)
    app.config.from_object('config.ProductionConfig')

    from .core.routes import blueprint as core_bp
    from .user.routes import blueprint as user_bp
    from .discord_verification.routes import blueprint as discord_bp
    from .quiz_support.routes import blueprint as quiz_support_bp
    
    app.register_blueprint(core_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(discord_bp)
    app.register_blueprint(quiz_support_bp)

    register_extensions(app)

    return app


def register_extensions(app: object) -> None:
    mail.init_app(app)
    bcrypt.init_app(app)
    database.init_app(app)
    login_manager.init_app(app)
    discord.init_app(app)

    from .discord_verification.models import User
    from .core.models import Announcements
    from .quiz_support.models import Quiz, Question, Variant

    tables = (User, Announcements, Quiz, Question, Variant)

    with app.app_context():
        engine = database.get_engine()

        database.create_all()
        database.session.commit()