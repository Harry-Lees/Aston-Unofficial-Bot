from app.extensions import database

class User(database.Model):
    __tablename__ = 'user_tab'

    id = database.Column(
        database.String(), # string not an int to ensure leading 0s are not stripped accidentally
        primary_key = True
    )

    email = database.Column( # aston.ac.uk Email address
        database.String(),
        index = True,
        unique = True,
        nullable = False,
    )

    verified = database.Column( # Whether the user has been verified or not
        database.Boolean,
        index = False,
        unique = False,
        nullable = False
    )