from flask import Blueprint, render_template, redirect, session, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.auth_guard import issue_session_token, revoke_session_token
from app.models import User, db
from app import limiter
from urllib.parse import urlparse
from datetime import datetime, timedelta
from app.email import generate_otp_code, send_otp_email
from app import bcrypt

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
@limiter.limit("5 per minute")                          # max 5 login attempts per minute per IP
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=bool(remember))
            issue_session_token(user)
            next_page = _safe_next_url(request.args.get('next'))
            flash('Welcome back to FREKS.', 'success')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per hour")                           # max 3 registrations per hour per IP
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()

        if not all([username, email, password, first_name, last_name]):
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')
        
        # Basic email format check; use a stronger validator in production
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

        code = generate_otp_code()
        user.otp_code_hash = bcrypt.generate_password_hash(code).decode('utf-8')
        user.otp_expires_at = datetime.utcnow() + timedelta(
            minutes=current_app.config['OTP_EXPIRY_MINUTES']
        )
        user.otp_last_sent_at = datetime.utcnow()
        user.otp_attempts = 0

        db.session.add(user)
        db.session.commit()

        send_otp_email(email, code)

        session['pending_otp_user_id'] = user.id
        flash('We sent a verification link to your email.', 'info')
        return redirect(url_for('auth.verify_otp'))

    return render_template('auth/register.html')


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def verify_otp():
    user_id = session.get('pending_otp_user_id')
    if not user_id:
        flash('No pending verification. Please register again.', 'danger')
        return redirect(url_for('auth.register'))

    user = User.query.get(user_id)
    if not user or user.email_verified:
        session.pop('pending_otp_user_id', None)
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        entered_code = request.form.get('code', '').strip()

        if not user.otp_code_hash or not user.otp_expires_at:
            flash('No active code. Please request a new one.', 'danger')
            return render_template('auth/verify_otp.html')

        if datetime.utcnow() > user.otp_expires_at:
            flash('Code expired. Please request a new one.', 'danger')
            return render_template('auth/verify_otp.html')

        if user.otp_attempts >= current_app.config['OTP_MAX_ATTEMPTS']:
            flash('Too many attempts. Please request a new code.', 'danger')
            return render_template('auth/verify_otp.html')

        if bcrypt.check_password_hash(user.otp_code_hash, entered_code):
            user.email_verified = True
            user.otp_code_hash = None
            user.otp_expires_at = None
            user.otp_attempts = 0
            db.session.commit()

            session.pop('pending_otp_user_id', None)
            login_user(user)
            issue_session_token(user)
            flash('Email verified. Welcome to FREKS.', 'success')
            return redirect(url_for('main.index'))
        else:
            user.otp_attempts += 1
            db.session.commit()
            flash('Incorrect code. Please try again.', 'danger')

    return render_template('auth/verify_otp.html')


@auth_bp.route('/resend-otp', methods=['POST'])
@limiter.limit("5 per hour")
def resend_otp():
    user_id = session.get('pending_otp_user_id')
    if not user_id:
        return redirect(url_for('auth.register'))

    user = User.query.get(user_id)
    if not user or user.email_verified:
        return redirect(url_for('auth.login'))

    cooldown = current_app.config['OTP_RESEND_COOLDOWN_SECONDS']
    if user.otp_last_sent_at and \
       (datetime.utcnow() - user.otp_last_sent_at).total_seconds() < cooldown:
        flash('Please wait before requesting another code.', 'danger')
        return redirect(url_for('auth.verify_otp'))

    code = generate_otp_code()
    user.otp_code_hash = bcrypt.generate_password_hash(code).decode('utf-8')
    user.otp_expires_at = datetime.utcnow() + timedelta(
        minutes=current_app.config['OTP_EXPIRY_MINUTES']
    )
    user.otp_last_sent_at = datetime.utcnow()
    user.otp_attempts = 0
    db.session.commit()

    send_otp_email(user.email, code)
    flash('A new code has been sent to your email.', 'info')
    return redirect(url_for('auth.verify_otp'))


@auth_bp.route('/logout')
@login_required
def logout():
    revoke_session_token(current_user)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
