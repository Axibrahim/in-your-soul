from urllib.parse import urlparse
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from app import limiter
from app.auth_guard import issue_session_token, revoke_session_token
from app.email import (
    confirm_reset_token,
    confirm_verify_token,
    generate_reset_token,
    generate_verify_token,
    send_reset_email,
    send_verification_email,
)
from app.models import User, db


def _safe_next_url(target):
    """Only allow redirecting to a relative, in-app path (blocks open-redirect)."""
    if not target:
        return None
    parsed = urlparse(target)
    if parsed.netloc or parsed.scheme:
        return None
    if not target.startswith('/') or target.startswith('//'):
        return None
    return target


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('5 per minute')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        user = User.query.filter(db.func.lower(User.username) == username).first()
        if user and user.check_password(password):
            if not user.email_verified:
                session['pending_verify_user_id'] = user.id
                flash('Please verify your email before logging in.', 'danger')
                return redirect(url_for('auth.check_email'))
            login_user(user, remember=bool(remember))
            issue_session_token(user)
            next_page = _safe_next_url(request.args.get('next'))
            flash('Welcome back.', 'success')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit('5 per hour')
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first() if email else None

        if user and user.email_verified:
            token = generate_reset_token(user.email)
            send_reset_email(user.email, token)

        flash(
            'If that verified email belongs to an account, a reset link has been sent.',
            'info',
        )
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
@limiter.limit('5 per hour')
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    email = confirm_reset_token(token)
    if not email:
        flash('That password reset link is invalid or expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first()
    if not user or not user.email_verified:
        flash('That password reset link is invalid or expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html', token=token)

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('auth/reset_password.html', token=token)

        user.set_password(password)
        user.session_token = None
        user.session_issued_at = None
        db.session.commit()
        flash('Your password has been reset. You can log in now.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit('3 per hour')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()

        if not all([username, email, phone, password, first_name, last_name]):
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')

        if '@' not in email or '.' not in email.split('@')[-1]:
            flash('Please enter a valid email address.', 'danger')
            return render_template('auth/register.html')

        if not phone.replace('+', '').replace(' ', '').isdigit() or len(phone) < 8:
            flash('Please enter a valid phone number.', 'danger')
            return render_template('auth/register.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter(db.func.lower(User.username) == username).first():
            flash('Username already taken.', 'danger')
            return render_template('auth/register.html')

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email_verified=False,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        token = generate_verify_token(email)
        send_verification_email(email, token, first_name=first_name)

        session['pending_verify_user_id'] = user.id
        flash('Check your email for a verification link.', 'info')
        return redirect(url_for('auth.check_email'))

    return render_template('auth/register.html')


@auth_bp.route('/check-email')
def check_email():
    if not session.get('pending_verify_user_id'):
        return redirect(url_for('auth.register'))
    return render_template('auth/check_email.html')


@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    print(f"[VERIFY DEBUG] Endpoint hit with token: {token}")

    email = confirm_verify_token(token)
    if not email:
        print("[VERIFY DEBUG] confirm_verify_token returned None (Invalid or Expired Token)")
        flash('That verification link is invalid or expired.', 'danger')
        return redirect(url_for('auth.resend_verification'))

    print(f"[VERIFY DEBUG] Decoded email: {email}")

    user = User.query.filter_by(email=email).first()
    if not user:
        print(f"[VERIFY DEBUG] No user found in DB for email: {email}")
        flash('Account not found.', 'danger')
        return redirect(url_for('auth.register'))

    print(f"[VERIFY DEBUG] User found (ID: {user.id}, email_verified: {user.email_verified})")

    session.pop('pending_verify_user_id', None)

    if user.email_verified:
        print("[VERIFY DEBUG] User is already verified. Redirecting...")
        login_user(user, remember=True)
        issue_session_token(user)
        flash('Email already verified. Welcome back!', 'info')
        return redirect(url_for('main.index'))

    # Update database record and commit transaction
    try:
        user.email_verified = True
        db.session.add(user)
        db.session.commit()
        print(f"[VERIFY DEBUG] Successfully updated user {user.id} email_verified to True")
    except Exception as e:
        db.session.rollback()
        print(f"[VERIFY DEBUG] Database commit failed: {e}")
        flash('Database update error. Please try again.', 'danger')
        return redirect(url_for('auth.login'))

    # Log user in and issue active session guard token
    login_user(user, remember=True)
    issue_session_token(user)

    flash('Email verified! You are now logged in.', 'success')
    return redirect(url_for('main.index'))


@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
@limiter.limit('5 per hour')
def resend_verification():
    if request.method == 'POST':
        user_id = session.get('pending_verify_user_id')
        user = User.query.get(user_id) if user_id else None
        if user and not user.email_verified:
            token = generate_verify_token(user.email)
            send_verification_email(user.email, token, first_name=user.first_name)
            flash('Verification email resent.', 'info')
        else:
            flash('Nothing to resend.', 'info')
        return redirect(url_for('auth.check_email'))
    return render_template('auth/resend_verification.html')


@auth_bp.route('/logout')
@login_required
def logout():
    revoke_session_token(current_user)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))