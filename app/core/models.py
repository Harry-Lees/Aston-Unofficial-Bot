from app.extensions import database

class Announcements(database.Model):
    __tablename__ = 'announcements_tab'

    id = database.Column(
        database.String(), # string not an int to ensure leading 0s are not stripped accidentally
        primary_key = True
    )

    title = database.Column(
        database.String(),
        nullable = False
    )

    created_date = database.Column(
        database.DateTime(),
        nullable = False
    )

    author = database.Column(
        database.String(),
        nullable = False
    )

    content = database.Column(
        database.String(),
        nullable = False
    )