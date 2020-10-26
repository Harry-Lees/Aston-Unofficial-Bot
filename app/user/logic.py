from itsdangerous import URLSafeTimedSerializer


'''
Program contains all processing used in routes.py
'''

__all__ = [
    'email_valid',
    'code_valid',
    'confirm_verification',
    'user_verified',
    'pending_user',
    'generate_confirmation_token',
    'confirm_token'
]

def email_valid(email_address: str) -> bool:
    address, domain = email_address.split('@')
    return domain == 'aston.ac.uk' and len(address) == 9


def code_valid(user_id: str, verification_code: str) -> bool:
    with psycopg2.connect(DATABASE_AUTH) as connection:
        cursor = connection.cursor()

        cursor.execute('SELECT uuid FROM pending_users WHERE id = ?', [user_id])
        return verification_code == cursor.fetchone()[0]


def confirm_verification(user_id: str, email_address: str) -> None:
    address, domain = email_address.split('@')
    is_student = address.isnumeric()

    with psycopg2.connect(DATABASE_AUTH) as connection:
        cursor = connection.cursor()

        cursor.execute('DELETE FROM pending_users WHERE id = ?', [user_id])
        cursor.execute('INSERT INTO user VALUES(?, ?, ?)', [user_id, email_address, is_student])
        connection.commit()


def user_verified(user_id: str) -> bool:
    with psycopg2.connect(**DATABASE_AUTH):
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM user WHERE id = ?', [user_id])
        return bool(cursor.fetchone())


def pending_user(user_id: str) -> bool:
    with psycopg2.connect(**DATABASE_AUTH):
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM pending_users WHERE id = ?', [user_id])
        return bool(cursor.fetchone())


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt = app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration: int = 3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False

    return email