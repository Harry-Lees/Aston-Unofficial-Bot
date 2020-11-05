from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class EmailVerification(FlaskForm):
    email = StringField('Email', validators = [DataRequired()])
    submit = SubmitField('Send Email')
