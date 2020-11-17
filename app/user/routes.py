from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import current_user, login_user, logout_user
from flask_discord import requires_authorization, Unauthorized

from app.extensions import bcrypt, database, discord
from .models import User
from .forms import LoginForm, RegisterForm

blueprint = Blueprint('user', __name__, template_folder = 'templates')


@blueprint.route('/callback')
def callback():
    discord.callback()
    return redirect(url_for('user.manage_server'))


@blueprint.route('/login')
def login():
    return discord.create_session(scope = ['identify', 'guilds'])


@blueprint.route('/logout')
@requires_authorization
def logout():
    discord.revoke()
    return redirect(url_for('core.index'))


@blueprint.route('/manage_server')
@requires_authorization
def manage_server():
    user = discord.fetch_user()
    guilds = discord.fetch_guilds()

    return render_template('server.html', user = user, guilds = guilds)


@blueprint.route('/profile')
@requires_authorization
def profile():
    user = discord.fetch_user()
    return render_template('profile.html', user = user)


@blueprint.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for('user.login'))