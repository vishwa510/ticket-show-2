from flask_mail import Mail, Message
from email.message import EmailMessage
import os
import smtplib
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl


mail = Mail()

SMTP_SERVER_HOST = 'mail.office365.com'
SMTP_SERVER_PORT = 587
SENDER_ADDRESS = 'mad2project@outlook.com'
SENDER_PASSWORD = 'secret10'

def configure_mail(app, mail_server, mail_port, mail_use_tls, mail_username, mail_password, mail_use_ssl):
    app.config['MAIL_SERVER'] = mail_server
    app.config['MAIL_PORT'] = mail_port
    app.config['MAIL_USE_TLS'] = mail_use_tls
    app.config['MAIL_USERNAME'] = mail_username
    # app.config['MAIL_DEFAULT_SENDER'] = mail_default_sender
    app.config['MAIL_PASSWORD'] = mail_password
    app.config['MAIL_USE_SSL'] = mail_use_ssl

    mail.init_app(app)


def send_email(to, subject, msg, attachment=None):
    mail = MIMEMultipart()
    mail["From"] = SENDER_ADDRESS
    mail["Subject"] = subject

    # Convert the list of recipients to a single string
    to_string = ", ".join(to)
    mail["To"] = to_string

    mail.attach(MIMEText(msg, "html"))

    if attachment is not None:
        # adding attachment file to mail body
        with open(attachment, "rb") as attachment_file:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment_file.read())
            encode_base64(part)

        part.add_header("Content-Disposition", f"attachment; filename={attachment}")
        mail.attach(part)

    # Configure the SSL context for Outlook
    context = ssl.create_default_context()

    try:
        # Connect to the server and send the email
        with smtplib.SMTP(SMTP_SERVER_HOST, SMTP_SERVER_PORT) as server:
            server.ehlo('shershaah')
            server.starttls(context=context)
            server.ehlo('shershaah')
            server.login(SENDER_ADDRESS, SENDER_PASSWORD)
            server.send_message(mail)

        # Remove the files from server space
        if attachment is not None:
            os.remove(attachment)

        return True
    except Exception as e:
        print("Error sending email:", str(e))
        return False
