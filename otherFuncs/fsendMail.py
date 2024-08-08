from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import smtplib
load_dotenv()
import os

def send_email(orig, cType, cOrder, cCoin, cBtext, idInstance):
    smtp_server = os.getenv('MAIL_SERVER')
    smtp_port = os.getenv('MAIL_PORT') 
    email_address = os.getenv('MAIL_ADDRESS')
    email_password = os.getenv('MAIL_APP_PASS')

    recipient = os.getenv('MAIL_RECIPIENT')
    subject = f"{orig} | {idInstance} "
    body = cBtext

    msg = MIMEMultipart()
    msg['From'] = f"ChristopherWalk | bID_{idInstance}"
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.add_header('X-Priority', '1')

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Starting TLS connection
        server.login(email_address, email_password)
        text = msg.as_string()
        server.sendmail(email_address, recipient, text)
        print('Email sent successfully!')
    except Exception as e:
        print(f'Failed to send email: {e}')
    finally:
        server.quit()
