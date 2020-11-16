from flask import Blueprint, render_template
from app.extensions import database
from .models import Announcements


blueprint = Blueprint('core', __name__, template_folder = 'templates')


@blueprint.route('/')
def index():
    announcements = Announcements.query.all()
    return render_template('index.html', announcements = announcements)


@blueprint.route('/feedback')
def feedback():
    return render_template('feedback.html')


@blueprint.route('/commands')
def commands():
    commands = [
        ['verify', 'Manually verify a user', 'verify @user'],
        ['get_link', 'Gets a users verification link', 'get_link @user'],
        ['self_link', 'Gets your own verification link', 'self_link'],
    ]

    return render_template('commands.html', commands = commands)


@blueprint.route('/status')
def status():
    return render_template('status.html')


@blueprint.route('/help')
def help_page():
    return render_template('help.html')


@blueprint.errorhandler(404)
def error_404():
    return render_template('error.html', error)