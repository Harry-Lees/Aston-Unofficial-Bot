from datetime import datetime

import psycopg2
from app.extensions import database
from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, session, url_for)
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadSignature, SignatureExpired

from .email import send_email
from .forms import EmailVerification
from .models import User
from app.discord_verification.models import User as discord_user

blueprint = Blueprint('discord', __name__, template_folder = 'templates', url_prefix = '/discord')


@blueprint.route('/verification_successful')
def verification_result():
    return render_template('verification_result.html')


@blueprint.route('/confirm/<token>', methods = ['GET', 'POST'])
def confirm_email(token: str):
    if email := confirm_token(token):
        user = User.query.filter_by(email = email).first_or_404()
    else:
        flash('The confirmation link is invalid or has expired', 'alert-danger')
        return redirect(url_for('discord.verification_result'))

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
            cursor.execute(f"NOTIFY {discord_user.__tablename__}, %(email)s", {'email' : email})
            connection.commit()

        print('NOTIFY sent')
        flash('You have been successfully verified! You can now continue to Discord. It may take several seconds for your roles to be assigned. If they have not been assigned within the next 5 minutes, please open a Ticket.', 'alert-success')

    return redirect(url_for('discord.verification_result'))


@blueprint.route('/register', methods = ['GET', 'POST'])
def verify_user():
    form = EmailVerification()

    if not (user_id := request.args.get('user_id', None)): # check if the user_id was provided
        flash('An error has occurred, if you clicked on the link from Discord, please contact a Discord admin, if you have just opened this page, please close your tab.', 'alert-danger')
        return render_template('discord_register.html', form = form)

    user = User.query.filter_by(id = user_id).first()

    if user:
        if user.verified:
            flash('You are already verified on this server.', 'alert-warning')
            return render_template('discord_register.html', form = form)
        flash('You have already started the verification process. If you have not received an email, please check your junk mail or click the link below.', 'alert-warning')
        return render_template('discord_register.html', form = form)

    if form.validate_on_submit():
        if email_valid(form.email.data):
            if form.email.data[:2] == '19':
                flash('2nd year and foundation students should contact a Moderator to be verified', 'alert-warning')
                return render_template('discord_register.html', form = form)
            elif form.email.data[:2] != '20':
                flash('Your email address is from an unrecognised year, please contact a Moderator to be verified', 'alert-warning')
                return render_template('discord_register.html', form = form)

            user = User(
                email = form.email.data,
                id = user_id,
                verified = False
            )

            database.session.add(user)
            database.session.commit()

            _send_email(form.email.data, user_id)
            flash(f'An email has been sent to {form.email.data}, you may now close this page.', 'alert-success')
        else:
            flash('Please enter a valid aston.ac.uk email address', 'alert-warning')

    return render_template('discord_register.html', form = form)


@blueprint.route('/resend', methods = ['GET', 'POST'])
def resend_email():
    user_id = request.args.get('user_id', None)

    user = User.query.filter_by(id = user_id).first()

    if user:
        _send_email(user.email, user_id)
        flash(f'An email has been resent to {user.email}, you may now close this page.', 'alert-success')
    else:
        flash('You haven\'t been sent an email yet. Please fill in the form to send an email', 'alert-warning')
    
    if user.email[:2] == '19':
        flash('2nd year and foundation students should contact a Moderator to be verified', 'alert-warning')
    elif form.email.data[:2] != '20':
        flash('Your email address is from an unrecognised year, please contact a Moderator to be verified', 'alert-warning')
    else:
        flash('Something went wrong. Please contact a Moderator')

    return render_template('verification_result.html')


def _send_email(email: str, user_id: str):
    # generate Email data
    token = generate_token(email)
    confirm_url = url_for('discord.confirm_email', token = token, _external = True)
    html = render_template('email.html', confirm_url = confirm_url)
    subject = 'Welcome to Aston Unofficial'
    
    send_email(current_app, email, subject, html)

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
    except BadSignature:
        print('something went wrong')
        return False
    except SignatureExpired:
        print('The confirmation link is invalid or has expired')
        return False

    return email


def email_valid(email_address: str) -> bool:
    split_message = email_address.split('@')

    if len(split_message) == 2:
        address, domain = split_message
        return domain == 'aston.ac.uk' and len(address) == 9
    else:
        return False