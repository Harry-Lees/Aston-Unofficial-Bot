from flask import Blueprint, render_template, flash, request, redirect
from flask_login import current_user, login_user, logout_user
from flask_discord import requires_authorization, Unauthorized

from app.extensions import bcrypt, database, discord
from .models import User
from .forms import LoginForm, RegisterForm

blueprint = Blueprint('user', __name__, template_folder = 'templates')


@blueprint.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace("http://", "https://", 1)
        return redirect(url, code = 301)

@blueprint.route('/callback/')
def callback():
    print('called')
    discord.callback()
    return redirect(url_for('user.me'))


@blueprint.route('/login')
def login():
    return discord.create_session(scope=['identify', 'guilds'])


@blueprint.route('/logout', methods = ['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('core.index'))


@blueprint.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("user.login"))


@blueprint.route('/me/')
def me():
    user = discord.fetch_user()
    return f"""
    <html>
        <head>
            <title>{user.name}</title>
        </head>
        <body>
            <img src='{user.avatar_url}' />
        </body>
    </html>"""


# @blueprint.route('/register', methods = ['GET', 'POST'])
# def register():
#     print('called')
#     print(request.method)
#     form = RegisterForm()

#     if current_user.is_authenticated:
#         print('already authenticated')
#         return redirect(url_for('core.index'))

#     if form.validate_on_submit():
#         print('valid form')
#         hashed_password = bcrypt.generate_password_hash(form.password.data)
#         user = User(username = form.username.data, email = form.email.data, password = hashed_password)

#         database.session.add(user)
#         database.session.commit()

#         flash('Sucessfully created account!')
#         return redirect(url_for('login'))

#     return render_template('register.html', form = form)

# @blueprint.route('/login', methods = ['GET', 'POST'])
# def login():
#     form = LoginForm()

#     if current_user.is_authenticated:
#         return redirect(url_for('core.setup'))

#     if form.validate_on_submit():
#         user = User.query.filter_by(username = form.username.data).first()

#         if not user:
#             flash('There is no user with that username, please try again.')
#             return render_template('login.html', form = form)

#         correct_password = bcrypt.check_password_hash(user.password, form.password.data)
#         if correct_password:
#             login_user(user, remember = form.remember.data)
#             return redirect(url_for('core.setup'))
#         else:
#             flash('Login unsuccessful, please check password.')

#     return render_template('login.html', form = form)