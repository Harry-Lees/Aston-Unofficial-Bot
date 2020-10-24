def email_valid(email_address: str) -> bool:
    address, domain = email_address.split('@')
    return domain == 'aston.ac.uk' and len(address) == 9

def code_valid(user_id: str, verification_code: str) -> bool:
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('SELECT uuid FROM pending_users WHERE id = ?', [user_id])
    return verification_code == cursor.fetchone()[0]

def confirm_verification(user_id: str, email_address: str) -> None:
    address, domain = email_address.split('@')
    is_student = address.isnumeric()

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('DELETE FROM pending_users WHERE id = ?', [user_id])
    cursor.execute('INSERT INTO user VALUES(?, ?, ?)', [user_id, email_address, is_student])
    connection.commit()

def assign_permissions():
    pass