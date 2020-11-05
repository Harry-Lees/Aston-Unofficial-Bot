from app.extensions import database, login_manager
from flask_login import UserMixin

class User(database.Model, UserMixin):
    __tablename__ = 'website_user_tab'


    email = database.Column( # aston.ac.uk Email address
        database.String(),
        primary_key = True,
    )


    username = database.Column(
        database.String(),
        nullable = False,
        unique = True,
    )


    password = database.Column(
        database.String(),
        nullable = False
    )


    verified = database.Column(
        database.Boolean,
        index = False,
        unique = False,
        nullable = False
    )


@login_manager.user_loader
def load_user(id: int) -> User:
    return User.query.get(int(id))