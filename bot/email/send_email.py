import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sender_email = 'astonunofficial@gmail.com'
receiver_email = 'harry.lees@gmail.com'
password = 'jox6DWAY@sqoc5hall'

message = MIMEMultipart('alternative')
message['Subject'] = 'test'
message['From'] = sender_email
message['To'] = receiver_email

# Create the plain-text and HTML version of your message
text = '''\
Hi,
How are you?
Real Python has many great tutorials:
www.realpython.com'''

html = '''\
<html>
    <body>
        <p>
            This is an email verification test!
            Please click <a href='localhost:5000/verify/'>Here</a> to verify your email.
        </p>
    </body>
</html>
'''

def send_email():
    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
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