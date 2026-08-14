from flask import Blueprint, render_template, redirect, session, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.auth_guard import issue_session_token, revoke_session_token
from app.models import User, db
from app import limiter
from urllib.parse import urlparse
from app.email import generate_verify_token, confirm_verify_token, send_verification_email


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
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if not user.email_verified:
                flash('Please verify your email before logging in.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user, remember=bool(remember))
            issue_session_token(user)
            next_page = _safe_next_url(request.args.get('next'))
            flash('Welcome back to FREKS.', 'success')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()

        if not all([username, email, password, first_name, last_name]):
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')

        if '@' not in email or '.' not in email.split('@')[-1]:
            flash('Please enter a valid email address.', 'danger')
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

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('auth/register.html')

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            email_verified=False,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        token = generate_verify_token(email)
        send_verification_email(email, token)

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
    email = confirm_verify_token(token)
    if not email:
        flash('That verification link is invalid or expired.', 'danger')
        return redirect(url_for('auth.resend_verification'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Account not found.', 'danger')
        return redirect(url_for('auth.register'))

    if not user.email_verified:
        user.email_verified = True
        db.session.commit()

    session.pop('pending_verify_user_id', None)
    login_user(user)
    issue_session_token(user)
    flash('Email verified. Welcome to FREKS.', 'success')
    return redirect(url_for('main.index'))


@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def resend_verification():
    if request.method == 'POST':
        user_id = session.get('pending_verify_user_id')
        user = User.query.get(user_id) if user_id else None
        if user and not user.email_verified:
            token = generate_verify_token(user.email)
            send_verification_email(user.email, token)
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