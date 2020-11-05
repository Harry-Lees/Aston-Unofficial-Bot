from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

# setup Database
database = SQLAlchemy()
Session = sessionmaker(bind = database)
session = Session()

# setup Mail
mail = Mail()

# setup login manager
login_manager = LoginManager()
login_manager.login_view = 'user.login'

bcrypt = Bcrypt()
