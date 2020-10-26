from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker

# setup Database
database = SQLAlchemy()
Session = sessionmaker(bind = database)
session = Session()

# setup Mail
mail = Mail()
