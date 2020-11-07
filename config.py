from os import getenv


class DiscordConfig:
    DISCORD_TOKEN = getenv('DISCORD_TOKEN')
    ADMIN_ROLE = 'Admin' # name of admin role
    STUDENT_2020_ROLE = '2020' # name of student 2020 role
    STUDENT_2019_ROLE = '2019' # name of student 2019 role
    LECTURER_ROLE = 'teacher' # name of lecturer role


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
    

class TestingConfig(Config):
    TESTING = True
