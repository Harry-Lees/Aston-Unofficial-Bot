import sqlite3

from bot.email.send_email import send_email
from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)

from .forms import EmailVerification, VerifyCode

blueprint = Blueprint('core', __name__, template_folder = 'templates')

@blueprint.route('/')
def return_index():
    return render_template('index.html')

@blueprint.route('/verification_successful')
def verification_successful():
    return render_template('successful_verification.html')

@blueprint.route('/verify', methods = ['GET', 'POST'])
def verify_code():
    form = VerifyCode()

    user_id = session.get('user_id')
    email_address = session.get('email_address')

    if form.validate_on_submit():
        if code_valid(user_id, form.verification_code.data):
            confirm_verification(user_id, email_address)
            return redirect(url_for('core.verification_successful'))
        else:
            flash('the code you entered was invalid')

    return render_template('verify_code.html', form = form)

@blueprint.route('/verify_user', methods = ['GET', 'POST'])
def verify_user():
    form = EmailVerification()
    user_id = request.args.get('user_id', None)

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM user WHERE id = ?', [user_id])
    if cursor.fetchone():
        flash('This account is already verified on this server.')
    else:
        cursor.execute('SELECT * FROM pending_users WHERE id = ?', [user_id])
        if cursor.fetchone():
            if form.validate_on_submit():
                if email_valid(form.email.data):
                    session['email_address'] = form.email.data
                    session['user_id'] = user_id
                    send_email(user_id, form.email.data)
                    return redirect(url_for('core.verify_code'))
                else:
                    flash('Please enter a valid aston.ac.uk email address.')
        else:
            flash('An unexpected error has occurred. Please close this tab and try again.')

    return render_template('verify_user.html', form = form)

def email_valid(email_address: str) -> bool:
    address, domain = email_address.split('@')
    return domain == 'aston.ac.uk' and len(address) == 9

def code_valid(user_id: str, verification_code: str) -> bool:
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('SELECT uuid FROM pending_users WHERE id = ?', [user_id])
    return verification_code == cursor.fetchone()[0]

def confirm_verification(user_id: str, email_address: str) -> None:
    address, domain = email_address.split('@')
    is_student = address.isnumeric()

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('DELETE FROM pending_users WHERE id = ?', [user_id])
    cursor.execute('INSERT INTO user VALUES(?, ?, ?)', [user_id, email_address, is_student])
    connection.commit()
