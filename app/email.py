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


def _resend_send_template(to_email: str, subject: str, template_id: str, variables: dict) -> bool:
    """Helper to send emails using Resend templates."""
    resend.api_key = os.environ.get('RESEND_API_KEY')
    from_email = os.environ.get('RESEND_FROM_EMAIL')

    if not resend.api_key or not from_email:
        print("RESEND_API_KEY or RESEND_FROM_EMAIL is not configured.")
        return False

    try:
        resend.Emails.send({
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "template": {
                "id": template_id,
                "variables": variables,
            },
        })
        return True
    except Exception as e:
        print(f"Failed to send email via Resend template: {e}")
        return False


def send_verification_email(to_email: str, token: str, first_name: str = "") -> bool:
    link = url_for('auth.verify_email', token=token, _external=True)
    
    variables = {
        "verification_url": link,
        "first_name": first_name or "Friend"
    }
    
    return _resend_send_template(
        to_email=to_email,
        subject='Verify your IN YOUR SOUL account',
        template_id='5801c34f-63fb-44fe-9fd5-819d352f24d7',
        variables=variables
    )


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
    
    resend.api_key = os.environ.get('RESEND_API_KEY')
    from_email = os.environ.get('RESEND_FROM_EMAIL')

    if not resend.api_key or not from_email:
        return False

    try:
        resend.Emails.send({
            "from": from_email,
            "to": [to_email],
            "subject": 'Reset your IN YOUR SOUL password',
            "text": body,
        })
        return True
    except Exception as e:
        print(f"Failed to send reset email: {e}")
        return False