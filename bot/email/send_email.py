import smtplib
import sqlite3
import ssl
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import url_for
from jinja2 import Template

sender_email = 'astonunofficial@gmail.com'
password = 'jox6DWAY@sqoc5hall'

message = MIMEMultipart('alternative')

message['Subject'] = 'Verify your Email!'
message['From'] = sender_email

def send_email(user_id: str, receiver_email: str) -> None:
    message['To'] = receiver_email

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute('SELECT uuid FROM pending_users WHERE id = ?', [user_id])
    verification_code = cursor.fetchone()[0]

    text = f'Your unique login code is: {verification_code}'

    template = Template(open('bot/static/email_template.html').read())
    formatted_template = template.render(verification_code = verification_code)

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(formatted_template, 'html')

    with open('bot/static/images/banner.png', 'rb') as file:
        msgImage = MIMEImage(file.read(), _subtype = 'png')

    msgImage.add_header('Content-ID', '<image1>')

    message.attach(msgImage)
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(sender_email, password)

        server.sendmail(
            sender_email, 
            receiver_email, 
            message.as_string()
        )
