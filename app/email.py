import os
import secrets
import smtplib
from email.message import EmailMessage


def generate_otp_code() -> str:
    """6-digit numeric OTP using a cryptographically secure RNG."""
    return f"{secrets.randbelow(1_000_000):06d}"


def send_otp_email(to_email: str, code: str) -> bool:
    """
    Send the OTP via Gmail SMTP. Expects GMAIL_ADDRESS and GMAIL_PASSWORD
    (an App Password, not your normal Gmail password) environment variables.
    Returns True on success, False on error.
    """
    gmail_user = os.environ.get('GMAIL_ADDRESS')
    gmail_password = os.environ.get('GMAIL_PASSWORD')

    if not all([gmail_user, gmail_password]):
        print("GMAIL credentials are not configured.")
        return False

    expiry_minutes = os.environ.get('OTP_EXPIRY_MINUTES', '5')
    subject = 'Your FREKS verification code'
    body = (
        f"Your FREKS verification code is {code}. "
        f"It expires in {expiry_minutes} minutes.\n\n"
        f"If you didn't request this, please ignore this email."
    )

    msg = EmailMessage()
    msg['Subject'] = subject
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