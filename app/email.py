import os
import resend
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


def _resend_send(to_email: str, subject: str, text_body: str) -> bool:
    resend.api_key = os.environ.get('RESEND_API_KEY')
    from_email = os.environ.get('RESEND_FROM_EMAIL')

    if not resend.api_key or not from_email:
        print("RESEND_API_KEY or RESEND_FROM_EMAIL is not configured.")
        return False

    try:
        resend.Emails.send({
            "from": from_email,
            "to": to_email,
            "subject": subject,
            "text": text_body,
        })
        return True
    except Exception as e:
        print(f"Failed to send email via Resend: {e}")
        return False


def send_verification_email(to_email: str, token: str) -> bool:
    link = url_for('auth.verify_email', token=token, _external=True)
    body = (
        f"Welcome to IN YOUR SOUL.\n\n"
        f"Click the link below to verify your email address. "
        f"It expires in 1 hour.\n\n{link}\n\n"
        f"If you didn't create this account, ignore this email."
    )
    return _resend_send(to_email, 'Verify your IN YOUR SOUL account', body)


def generate_reset_token(email: str) -> str:
    return _serializer().dumps(email, salt='password-reset')


def confirm_reset_token(token: str):
    """Returns the email if valid and not expired, else None."""
    try:
        return _serializer().loads(
            token,
            salt='password-reset',
            max_age=current_app.config['PASSWORD_RESET_MAX_AGE_SECONDS'],
        )
    except Exception:
        return None


def send_reset_email(to_email: str, token: str) -> bool:
    link = url_for('auth.reset_password', token=token, _external=True)
    body = (
        f"We received a request to reset your IN YOUR SOUL password.\n\n"
        f"Click the link below to set a new password. It expires in 30 minutes.\n\n{link}\n\n"
        f"If you didn't request this, you can safely ignore this email — "
        f"your password will not be changed."
    )
    return _resend_send(to_email, 'Reset your IN YOUR SOUL password', body)