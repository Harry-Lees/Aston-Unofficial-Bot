from app import create_app
from os import getenv

app = create_app()

__author__ = 'Harry Lees'
__date__ = '20.10.2020'

if __name__ == '__main__':
    print(getenv('PORT'))
    app.run(host='0.0.0.0', port = getenv('PORT', 5000))