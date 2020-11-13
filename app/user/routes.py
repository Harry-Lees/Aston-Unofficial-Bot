from flask import Blueprint, render_template, flash, request, redirect
from flask_login import current_user, login_user, logout_user
from flask_discord import requires_authorization, Unauthorized

from app.extensions import bcrypt, database, discord
from .models import User
from .forms import LoginForm, RegisterForm

blueprint = Blueprint('user', __name__, template_folder = 'templates')


@blueprint.route('/callback')
def callback():
    discord.callback()
    return redirect(url_for('user.me'))


@blueprint.route('/login')
def login():
    return discord.create_session(scope = ['identify', 'guilds'])


@blueprint.route('/logout')
@requires_authorization
def logout():
    discord.revoke()
    return redirect(url_for('core.index'))


@blueprint.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("user.login"))


@blueprint.route('/me')
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