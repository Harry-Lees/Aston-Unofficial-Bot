from flask import Blueprint, render_template


blueprint = Blueprint('core', __name__, template_folder = 'templates')


@blueprint.route('/')
def return_index():
    return render_template('index.html')


@blueprint.route('/example')
def return_example():
    return render_template('example.html')