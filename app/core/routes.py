from flask import Blueprint, render_template
from app.extensions import database
from .models import Announcements


blueprint = Blueprint('core', __name__, template_folder = 'templates')


@blueprint.route('/')
def return_index():
    announcements = Announcements.query.all()
    return render_template('index.html', announcements = announcements)


@blueprint.route('/feedback')
def feedback():
    return render_template('feedback.html')


@blueprint.errorhandler(404)
def error_404():
    return render_template('error.html', error)