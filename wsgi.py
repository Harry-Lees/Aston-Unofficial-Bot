from app import create_app

app = create_app()

__author__ = 'Harry Lees'
__date__ = '20.10.2020'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
