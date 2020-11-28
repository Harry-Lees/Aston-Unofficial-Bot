from app.extensions import database

class Quiz(database.Model):
    __tablename__ = 'quiz_tab'

    id = database.Column(
        database.Integer,
        primary_key = True,
        autoincrement = True
    )

    type = database.Column(
        database.String,
        nullable = False
    )

    title = database.Column(
        database.String,
        nullable = False,
        unique = True
    )

    questions = database.relationship(
        'Question',
        backref = 'quiz',
    )


class Question(database.Model):
    __tablename__ = 'questions_tab'

    id = database.Column(
        database.Integer,
        primary_key = True,
        autoincrement = True,
        unique = True
    )

    question_id = database.Column(
        database.Integer,
        primary_key = True
    )

    quiz_id = database.Column(
        database.Integer,
        database.ForeignKey('quiz_tab.id'),
        primary_key = True
    )

    variants = database.relationship(
        'Variant',
        backref = 'question',
    )


class Variant(database.Model):
    __tablename__ = 'variants_tab'

    id = database.Column(
        database.Integer,
        primary_key = True,
        autoincrement = True
    )

    question_id = database.Column(
        database.Integer,
        database.ForeignKey('questions_tab.id')
    )


    description = database.Column(
        database.String,
        nullable = True
    )

    transcript = database.Column(
        database.String,
        nullable = True
    )

    answer = database.Column(
        database.String,
        nullable = False
    )