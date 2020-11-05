from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, BooleanField, StringField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from .models import User


class RegisterForm(FlaskForm):
    username = StringField(
        'Username',
        validators = [DataRequired()]
    )

    email = StringField(
        'Email',
        validators = [DataRequired()]
    )

    password = PasswordField(
        'Password', 
        validators=[DataRequired()]
    )
    
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')]
    )

    submit = SubmitField('Register')


    def validate_user(self, username):
        user = User.query.filter_by(username = username.data).first()

        if user:
            print('existing user')
            raise ValidationError('A user already exists with that username')


    def validate_email(self, email) -> None:
        try:
            e, domain = email.data.split('@')
            print(e)
            print(domain)
        except ValueError:
            raise ValidationError('your email must include an @ symbol')

        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('There is already a user with that email address')

        if len(e) != 9 or not e.isnumeric:
            print('error (LENGTH)')
            raise ValidationError('Please input a valid @aston.ac.uk email address')

        if not domain == 'aston.ac.uk':
            print('error (DOMAIN)')
            raise ValidationError('Please input a valid @aston.ac.uk email address')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    
    remember = BooleanField('RememberMe')
    
    submit = SubmitField('Login')