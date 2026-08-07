from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from app.models import db, User, ActivityLog
from app.utils.helpers import sanitize_html

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))
        
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        
        if user and user.is_locked():
            flash('Account is temporarily locked due to multiple failed attempts. Try again later.', 'danger')
            return render_template('admin/login.html')
        
        if user and user.check_password(password) and user.is_active:
            user.login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=remember)
            
            # Log activity
            log = ActivityLog(
                user_id=user.id,
                action='login',
                details='User logged in',
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string[:255] if request.user_agent else ''
            )
            db.session.add(log)
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        else:
            if user:
                user.login_attempts = (user.login_attempts or 0) + 1
                if user.login_attempts >= 5:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                db.session.commit()
            flash('Invalid username or password.', 'danger')
    
    return render_template('admin/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    log = ActivityLog(
        user_id=current_user.id,
        action='logout',
        details='User logged out',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current = request.form.get('current_password')
        new_pass = request.form.get('new_password')
        confirm = request.form.get('confirm_password')
        
        if not current_user.check_password(current):
            flash('Current password is incorrect.', 'danger')
        elif new_pass != confirm:
            flash('New passwords do not match.', 'danger')
        elif len(new_pass) < 6:
            flash('Password must be at least 6 characters.', 'danger')
        else:
            current_user.set_password(new_pass)
            db.session.commit()
            flash('Password changed successfully.', 'success')
            return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/change_password.html')
