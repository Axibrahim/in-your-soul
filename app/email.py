import os
import smtplib
from email.message import EmailMessage
from flask import current_app, url_for
from itsdangerous import URLSafeTimedSerializer


def _serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


def generate_verify_token(email: str) -> str:
    return _serializer().dumps(email, salt='email-verify')


def confirm_verify_token(token: str):
    """Returns the email if the token is valid and not expired, else None."""
    try:
        return _serializer().loads(
            token,
            salt='email-verify',
            max_age=current_app.config['EMAIL_VERIFY_MAX_AGE_SECONDS'],
        )
    except Exception:
        return None


def send_verification_email(to_email: str, token: str) -> bool:
    gmail_user = os.environ.get('GMAIL_ADDRESS')
    gmail_password = os.environ.get('GMAIL_PASSWORD')

    if not all([gmail_user, gmail_password]):
        print("GMAIL credentials are not configured.")
        return False

    link = url_for('auth.verify_email', token=token, _external=True)
    body = (
        f"Welcome to FREKS.\n\n"
        f"Click the link below to verify your email address. "
        f"It expires in 1 hour.\n\n{link}\n\n"
        f"If you didn't create this account, ignore this email."
    )

    msg = EmailMessage()
    msg['Subject'] = 'Verify your FREKS account'
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(gmail_user, gmail_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send verification email: {e}")
        return False