from os import getenv
import os

class DiscordConfig:
    ADMIN_ROLE = 'Mod' # name of admin role
    STUDENT_2020_ROLE = '2020' # name of student 2020 role
    STUDENT_2019_ROLE = '2019' # name of student 2019 role
    LECTURER_ROLE = 'Aston Staff' # name of lecturer role


class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = getenv('SECRET_KEY')
    SECURITY_PASSWORD_SALT = getenv('SECURITY_PASSWORD_SALT')

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    MAIL_USERNAME = getenv('MAIL_USERNAME')
    MAIL_PASSWORD = getenv('MAIL_PASSWORD')

    MAIL_DEFAULT_SENDER = getenv('MAIL_USERNAME')

    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URL')

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = False

    CSRF_ENABLED = True

    DISCORD_CLIENT_ID = getenv('DISCORD_CLIENT_ID')
    DISCORD_CLIENT_SECRET = getenv('DISCORD_CLIENT_SECRET')
    DISCORD_REDIRECT_URI = getenv('DISCORD_REDIRECT_URI')
    DISCORD_BOT_TOKEN = getenv('DISCORD_BOT_TOKEN')

class HerokuConfig(Config):
    SQLALCHEMY_DATABASE_URI = ''
    

class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    OAUTHLIB_INSECURE_TRANSPORT = 'true'
    

class TestingConfig(Config):
    TESTING = True
