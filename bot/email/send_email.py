import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

sender_email = 'astonunofficial@gmail.com'
receiver_email = 'harry.lees@gmail.com'
password = input('please enter password: ')

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

def send_email(uuid: str) -> None:
    html = f'''\
    <html>
        <head>
            <style>
                .button {{
                    background-color: #0275D8;
                    border: none;
                    color: white;
                    padding: 15px 32px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;
                    cursor: pointer;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body style = 'font-family: Helvetica; color: black;'>
            <div style = 'margin: auto; width: 40%; max-width: 1200px; text-align: center; background-color: whitesmoke; border-radius: 5px; height: 75vh;'>
                <img src = 'cid:image1' style = 'width: 100%'><br>
                <h2>Email Confirmation</h2>
                <p>Please click the link below to get into the Aston Unofficial Discord server.</p>
                <a class = 'button' href = 'http://localhost:5000/verify?verification_code{uuid}'>
                    Verify your email
                </a>
            </div>
        </body>
    </html>
    '''

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    fp = open('../static/images/banner.png', 'rb')
    msgImage = MIMEImage(fp.read(), _subtype = 'png')
    fp.close()

    # Define the image's ID as referenced above
    msgImage.add_header('Content-ID', '<image1>')

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
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

if __name__ == '__main__':
    send_email('10')