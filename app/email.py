import os
import sys
import resend
from flask import current_app, url_for
from itsdangerous import URLSafeTimedSerializer


def _serializer():
    secret = current_app.config['SECRET_KEY']
    if not secret:
        raise RuntimeError("SECRET_KEY is not configured.")
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


def _resend_send_template(
    to_email: str,
    template_id: str,
    variables: dict
) -> bool:

    resend.api_key = os.environ.get('RESEND_API_KEY')
    from_email = os.environ.get('RESEND_FROM_EMAIL')

    if not resend.api_key or not from_email:
        print(
            "[RESEND ERROR] Missing API Key or From Email environment variables.",
            file=sys.stderr,
            flush=True
        )
        return False

    try:
        resend.Emails.send({
            "from": from_email,
            "to": [to_email],
            "template": {
                "id": template_id,
                "variables": variables,
            },
        })
        return True

    except Exception as e:
        print(
            f"[RESEND ERROR] Failed to send template email: {e}",
            file=sys.stderr,
            flush=True
        )
        return False


def send_verification_email(to_email: str, token: str, first_name: str = "") -> bool:
    base_url = os.environ.get('BASE_URL', 'https://inyoursoul.store').rstrip('/')
    
    try:
        path = url_for('auth.verify_email', token=token)
    except Exception:
        path = f"/verify-email/{token}"

    full_link = f"{base_url}{path}"
    
    print(f"[EMAIL DEBUG] Verification URL generated: {full_link}", file=sys.stderr, flush=True)

    variables = {
        "verification_url": full_link,
        "first_name": first_name or "Friend"
    }

    return _resend_send_template(
        to_email=to_email,
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
    base_url = os.environ.get('BASE_URL', 'https://inyoursoul.store').rstrip('/')
    try:
        path = url_for('auth.reset_password', token=token)
    except Exception:
        path = f"/reset-password/{token}"

    link = f"{base_url}{path}"
    print(f"[EMAIL DEBUG] Reset URL generated: {link}", file=sys.stderr, flush=True)

    body = (
        f"We received a request to reset your IN YOUR SOUL password.\n\n"
        f"Click the link below to set a new password. It expires in 30 minutes.\n\n{link}\n\n"
        f"If you didn't request this, you can safely ignore this email — "
        f"your password will not be changed."
    )

    resend.api_key = os.environ.get('RESEND_API_KEY')
    from_email = os.environ.get('RESEND_FROM_EMAIL')

    if not resend.api_key or not from_email:
        print(
            "[RESEND ERROR] Missing API Key or From Email environment variables.",
            file=sys.stderr,
            flush=True
        )
        return False

    try:
        resend.Emails.send({
            "from": from_email,
            "to": [to_email],
            "subject": "Reset your IN YOUR SOUL password",
            "text": body,
        })
        return True

    except Exception as e:
        print(
            f"[RESEND ERROR] Failed to send reset email: {e}",
            file=sys.stderr,
            flush=True
        )
        return False


def send_order_status_email(
    to_email: str, 
    order_id: str, 
    order_status: str = "Processing", 
    estimated_delivery: str = "3-5 Business Days", 
    first_name: str = ""
) -> bool:
    base_url = os.environ.get('BASE_URL', 'https://inyoursoul.store').rstrip('/')
    
    try:
        path = url_for('account.track_order', order_number=order_id)
    except Exception:
        path = f"/track-order/{order_id}"

    # Keep the full valid URL with protocol intact
    full_link = f"{base_url}{path}"
    
    resend.api_key = os.environ.get('RESEND_API_KEY')
    from_email = os.environ.get('RESEND_ORDERS_FROM_EMAIL')

    if not resend.api_key or not from_email:
        print("[RESEND ERROR] Missing API Key or From Email.", file=sys.stderr, flush=True)
        return False

    variables = {
        "order_tracking_url": f"{base_url}{path}",  # Output: https://inyoursoul.store/track-order/123
        "order_id": order_id,                       # Send as number or string matching template type
        "order_status": order_status,
        "estimated_delivery": estimated_delivery,
        "first_name": first_name or "Friend"
    }
    try:
        response = resend.Emails.send({
            "from": from_email,
            "to": [to_email],
            "subject": f"Update on your order #{order_id}",
            "template": {
                "id": "39d43d95-5733-456e-9c11-a81dd81e5eaa",
                "variables": variables,
            },
        })
        print(f"[RESEND SUCCESS] Order status email sent: {response}", file=sys.stderr, flush=True)
        return True

    except Exception as e:
        print(f"[RESEND ERROR] Failed to send order status email: {e}", file=sys.stderr, flush=True)
        return False