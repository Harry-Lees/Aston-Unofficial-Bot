from app import create_app
from os import getenv
from werkzeug.middleware.proxy_fix import ProxyFix 

app = create_app()
app = ProxyFix(app, x_for=1, x_host=1)

__author__ = 'Harry Lees'
__date__ = '20.10.2020'

print(getenv('PORT'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = getenv('PORT', 5000))