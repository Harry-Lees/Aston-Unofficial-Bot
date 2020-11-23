from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField, RadioField, FileField, SelectField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from .models import Quiz, Question, Variant


class QuizForm(FlaskForm):
    title = StringField('Title', validators = [DataRequired()])
    num_questions = IntegerField('Number of Questions', validators = [DataRequired()])

    quiz_type = RadioField(
        'Quiz Type',
        choices = [
            ['CS', 'Computer Systems'],
            ['Maths', 'Mathematics for Computing Professionals']
        ]
    )

    submit = SubmitField('Add Quiz')


class AnswerForm(FlaskForm):
    quiz = QuerySelectField(
        'Quiz',
        query_factory = lambda : Quiz.query,
        get_label = 'title',
        allow_blank = False
    )
    
    question = SelectField(
        'Question',
        choices = [[i, i] for i in range(1, 11)]
    )


    file = FileField()


    description = TextAreaField('Short description of the question')
    transcript = TextAreaField('Question screenshot transcript')
    answer = TextAreaField('The question answer', validators = [DataRequired()])

    submit = SubmitField('Add Answer')