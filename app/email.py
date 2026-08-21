import os
import sys
import resend
from flask import current_app, url_for
from itsdangerous import URLSafeTimedSerializer


def _serializer():
    # Use config SECRET_KEY or fall back to an environment key so worker nodes share tokens identically
    secret = current_app.config.get('SECRET_KEY') or os.environ.get('SECRET_KEY', 'default-fallback-secret-key')
    return URLSafeTimedSerializer(secret)


def generate_verify_token(email: str) -> str:
    return _serializer().dumps(email, salt='email-verify')


def confirm_verify_token(token: str):
    """Returns the email if the token is valid and not expired, else None."""
    try:
        max_age = current_app.config.get('EMAIL_VERIFY_MAX_AGE_SECONDS', 3600)
        return _serializer().loads(
            token,
            salt='email-verify',
            max_age=max_age,
        )
    except Exception as e:
        print(f"[TOKEN ERROR] Verification failed: {e}", file=sys.stderr, flush=True)
        return None


def _resend_send_template(to_email: str, subject: str, template_id: str, variables: dict) -> bool:
    """Helper to send emails using Resend templates."""
    resend.api_key = os.environ.get('RESEND_API_KEY')
    from_email = os.environ.get('RESEND_FROM_EMAIL')

    if not resend.api_key or not from_email:
        print("[RESEND ERROR] Missing API Key or From Email environment variables.", file=sys.stderr, flush=True)
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
        print(f"[RESEND ERROR] Failed to send template email: {e}", file=sys.stderr, flush=True)
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
        max_age = current_app.config.get('PASSWORD_RESET_MAX_AGE_SECONDS', 1800)
        return _serializer().loads(
            token,
            salt='password-reset',
            max_age=max_age,
        )
    except Exception as e:
        print(f"[TOKEN ERROR] Reset confirmation failed: {e}", file=sys.stderr, flush=True)
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
        print("[RESEND ERROR] Missing API Key or From Email environment variables.", file=sys.stderr, flush=True)
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
        print(f"[RESEND ERROR] Failed to send reset email: {e}", file=sys.stderr, flush=True)
        return False