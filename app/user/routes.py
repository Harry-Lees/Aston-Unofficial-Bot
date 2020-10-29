from datetime import datetime

import psycopg2
from app.extensions import database
from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, session, url_for)
from itsdangerous import URLSafeTimedSerializer

from .email import send_email
from .forms import EmailVerification
from .models import User

blueprint = Blueprint('user', __name__, template_folder = 'templates', url_prefix = '/user')


@blueprint.route('/verification_successful')
def verification_result():
    return render_template('verification_result.html')


@blueprint.route('/confirm/<token>', methods = ['GET', 'POST'])
def confirm_email(token: str):
    if email := confirm_token(token):
        user = User.query.filter_by(email = email).first_or_404()
    else:
        flash('The confirmation link is invalid or has expired', 'alert-danger')

    if user.verified:
        flash('You have already been verified on this server', 'alert-warning')
    else:
        user.verified = True

        database.session.add(user)
        database.session.commit()

        # send a notify to the database which can be picked up by the Discord bot
        database_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        with psycopg2.connect(database_uri) as connection:
            cursor = connection.cursor()
            cursor.execute(f"NOTIFY user_tab, %(email)s", {'email' : email})
            connection.commit()

        flash('You have been successfully verified! You can now continue to Discord. It may take several seconds for your roles to be assigned. If they have not been assigned within the next 5 minutes, please open a Ticket.', 'alert-success')

    return redirect(url_for('user.verification_result'))

@blueprint.route('/register', methods = ['GET', 'POST'])
def verify_user():
    form = EmailVerification()

    if not (user_id := request.args.get('user_id', None)): # check if the user_id was provided
        flash('an error has occurred, if you clicked on the link from Discord, please contact a Discord admin, if you have just opened this page, please close your tab.', 'alert-danger')
        return render_template('register.html', form = form)

    user = User.query.filter_by(id = user_id).first()
    if user:
        flash('you are already verified on this server.', 'alert-warning')
        return render_template('register.html', form = form)

    if form.validate_on_submit():
        if email_valid(form.email.data):
            user = User(
                email = form.email.data,
                id = user_id,
                verified = False
            )

            database.session.add(user)
            database.session.commit()

            # generate Email data
            token = generate_token(user.email)
            confirm_url = url_for('user.confirm_email', token = token, _external = True)
            html = render_template('email.html', confirm_url = confirm_url)
            subject = 'Welcome to Aston Unofficial'
            
            send_email(current_app, user.email, subject, html)
            flash(f'an email has been sent to {user.email}, you may now close this page.', 'alert-success')
        else:
            flash('please enter a valid aston.ac.uk email address', 'alert-warning')

    return render_template('register.html', form = form)


def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt = current_app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration: int = 3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt = current_app.config['SECURITY_PASSWORD_SALT'],
            max_age = expiration
        )
    except:
        return False

    return email


def email_valid(email_address: str) -> bool:
    split_message = email_address.split('@')

    if len(split_message) == 2:
        address, domain = split_message
        return domain == 'aston.ac.uk' and len(address) == 9
    else:
        return False
