import os


class DiscordConfig:
    DISCORD_TOKEN = 'NzY4MTI0NzI1MDk1NDMyMjAy.X4755Q.x3B9ht-yfgrvbwERYQU_j5CvY04'
    ADMIN_ROLE = '' # name of admin role
    STUDENT_ROLE = 'Student' # name of student role
    LECTURER_ROLE = 'teacher' # name of lecturer


class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'something very secret here'
    SECURITY_PASSWORD_SALT = 'secret salt'

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    MAIL_USERNAME = 'astonunofficial@gmail.com'
    MAIL_PASSWORD = 'jox6DWAY@sqoc5hall'

    MAIL_DEFAULT_SENDER = 'astonunofficial@gmail.com'

    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@database/DiscordDatabase'
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


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
