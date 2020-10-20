from flask import render_template, Blueprint, request

blueprint = Blueprint('core', __name__, template_folder = 'templates')

@blueprint.route('/')
def return_index():
    return render_template('index.html')

@blueprint.route('/verify', methods = ['GET', 'POST'])
def verify_email():
    verification_code = request.args.get('verification_code', None)

    if verification_code:
        return render_template('verify.html')
    else:
        return 'An error has occurred'
