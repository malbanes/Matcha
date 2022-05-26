# project/email_mngr.py

from flask_mail import Message

def send_email(to, subject, template):
    from main import app, mail
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender="noreply42project@yahoo.com"
    )
    mail.send(msg)