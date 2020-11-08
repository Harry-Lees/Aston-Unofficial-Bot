from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from flask_discord import DiscordOAuth2Session

# Setup Database
database = SQLAlchemy()
Session = sessionmaker(bind = database)
session = Session()

# Setup Mail
mail = Mail()

# Setup Login Manager
login_manager = LoginManager()
login_manager.login_view = 'user.login'

bcrypt = Bcrypt()

# Setup OAuth2
discord = DiscordOAuth2Session()