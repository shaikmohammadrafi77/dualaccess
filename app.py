import os
from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

from config import Config
from models import db, User, File, Transaction, KeyRequest
from forms import RegistrationForm, LoginForm, UploadForm
from abe_utils import encrypt_file, decrypt_file

# Flask App Initialization
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Ensure uploads folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Homepage
@app.route('/')
def index():
    return render_template('index.html')

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    flash('Self-registration is disabled. Please login with provided credentials.', 'info')
    return redirect(url_for('login'))

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=bool(getattr(form, 'remember_me', False).data), force=True)
            flash(f'Welcome, {user.username}!', 'success')
            # Redirect based on role
            if user.role == 'owner':
                return redirect(url_for('owner_dashboard'))
            elif user.role == 'enduser':
                return redirect(url_for('enduser_dashboard'))
            elif user.role == 'authority':
                return redirect(url_for('authority_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Login Failed. Check Username/Password.', 'danger')
    return render_template('login.html', form=form)

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Owner Dashboard
@app.route('/owner', methods=['GET', 'POST'])
@login_required
def owner_dashboard():
    if current_user.role != 'owner':
        flash('Unauthorized Access!', 'danger')
        return redirect(url_for('index'))
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        encrypted_path = encrypt_file(filepath, form.access_policy.data)
        new_file = File(filename=filename, owner_id=current_user.id, access_policy=form.access_policy.data, encrypted_path=encrypted_path)
        db.session.add(new_file)
        db.session.commit()
        # create pending requests for all end users
        end_users = User.query.filter_by(role='enduser').all()
        for eu in end_users:
            if not KeyRequest.query.filter_by(user_id=eu.id, file_id=new_file.id).first():
                db.session.add(KeyRequest(user_id=eu.id, file_id=new_file.id, status='Pending', request_time=datetime.utcnow()))
        db.session.commit()
        flash('File uploaded and encrypted successfully!', 'success')
        return redirect(url_for('owner_dashboard'))
    files = File.query.filter_by(owner_id=current_user.id).all()
    return render_template('dashboards/owner_dashboard.html', form=form, files=files)

# Delete File (Owner only)
@app.route('/delete_file/<int:file_id>')
@login_required
def delete_file(file_id):
    if current_user.role != 'owner':
        flash('Unauthorized Access!', 'danger')
        return redirect(url_for('index'))
    
    file = File.query.get_or_404(file_id)
    
    # Check if the file belongs to the current owner
    if file.owner_id != current_user.id:
        flash('You can only delete your own files!', 'danger')
        return redirect(url_for('owner_dashboard'))
    
    # Mark file as deleted instead of actually deleting it
    file.deleted = True
    file.deleted_at = datetime.utcnow()
    
    # Also mark all related key requests as rejected
    key_requests = KeyRequest.query.filter_by(file_id=file_id).all()
    for req in key_requests:
        if req.status == 'Pending':
            req.status = 'Rejected'
            req.response_time = datetime.utcnow()
    
    db.session.commit()
    flash(f'File "{file.filename}" has been deleted successfully!', 'success')
    return redirect(url_for('owner_dashboard'))

# End User Dashboard
@app.route('/enduser')
@login_required
def enduser_dashboard():
    if current_user.role != 'enduser':
        flash('Unauthorized Access!', 'danger')
        return redirect(url_for('index'))
    files = File.query.filter_by(deleted=False).all()  # Only show non-deleted files
    # Latest request per file for this user
    latest_requests = {}
    for f in files:
        req = (
            KeyRequest.query
            .filter_by(user_id=current_user.id, file_id=f.id)
            .order_by(KeyRequest.request_time.desc())
            .first()
        )
        latest_requests[f.id] = req
    return render_template('dashboards/enduser_dashboard.html', files=files, latest_requests=latest_requests)

# File download with approval verification
@app.route('/download/<int:file_id>')
@login_required
def download(file_id):
    file = File.query.get_or_404(file_id)
    
    # Check if file is deleted
    if file.deleted:
        flash('This file has been deleted and is no longer available.', 'danger')
        return redirect(url_for('enduser_dashboard'))
    
    is_owner = current_user.id == file.owner_id
    is_admin = current_user.role == 'admin'
    approved_req = (
        KeyRequest.query
        .filter_by(user_id=current_user.id, file_id=file.id, status='Approved')
        .first()
    )
    # Basic policy check: if file policy mentions a role, require user to match role
    policy = (file.access_policy or '').lower()
    role_ok = True
    if 'enduser' in policy:
        role_ok = current_user.role == 'enduser'
    elif 'owner' in policy:
        role_ok = current_user.role == 'owner'
    elif 'admin' in policy:
        role_ok = current_user.role == 'admin'
    elif 'authority' in policy:
        role_ok = current_user.role == 'authority'

    if not (is_owner or is_admin or (approved_req and role_ok)):
        flash('ACCESS DENIED BY THE ADMIN', 'danger')
        return redirect(url_for('enduser_dashboard'))
    decrypted_path = decrypt_file(file.encrypted_path, current_user.attributes)
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], path=os.path.basename(decrypted_path), as_attachment=True)

# End user: request access to a file
@app.route('/request/<int:file_id>')
@login_required
def request_access(file_id):
    if current_user.role != 'enduser':
        flash('Only end users can request access.', 'danger')
        return redirect(url_for('index'))
    file = File.query.get_or_404(file_id)
    existing = (
        KeyRequest.query
        .filter_by(user_id=current_user.id, file_id=file.id, status='Pending')
        .first()
    )
    if existing:
        flash('Request already pending.', 'info')
        return redirect(url_for('enduser_dashboard'))
    new_req = KeyRequest(user_id=current_user.id, file_id=file.id, status='Pending', request_time=datetime.utcnow())
    db.session.add(new_req)
    db.session.commit()
    flash('Access request submitted.', 'success')
    return redirect(url_for('enduser_dashboard'))

# Authority Dashboard
@app.route('/authority')
@login_required
def authority_dashboard():
    if current_user.role != 'authority':
        flash('Unauthorized Access!', 'danger')
        return redirect(url_for('index'))
    requests = KeyRequest.query.join(File).filter(File.deleted == False).order_by(KeyRequest.request_time.desc()).all()  # Only show requests for non-deleted files
    files = File.query.filter_by(deleted=False).all()  # Only show non-deleted files
    return render_template('dashboards/authority_dashboard.html', requests=requests, files=files)

# Admin Dashboard
@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Unauthorized Access!', 'danger')
        return redirect(url_for('index'))
    users = User.query.all()
    files = File.query.filter_by(deleted=False).all()  # Only show non-deleted files
    pending = KeyRequest.query.join(File).filter(File.deleted == False).order_by(KeyRequest.request_time.desc()).all()  # Only show requests for non-deleted files
    return render_template('dashboards/admin_dashboard.html', users=users, files=files, requests=pending)

# Admin approve/reject key requests
@app.route('/admin/approve/<int:req_id>')
@login_required
def admin_approve(req_id):
    if current_user.role != 'admin':
        flash('Unauthorized Access!', 'danger')
        return redirect(url_for('index'))
    req = KeyRequest.query.get_or_404(req_id)
    req.status = 'Approved'
    req.response_time = datetime.utcnow()
    db.session.commit()
    flash('Request approved.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/<int:req_id>')
@login_required
def admin_reject(req_id):
    if current_user.role != 'admin':
        flash('Unauthorized Access!', 'danger')
        return redirect(url_for('index'))
    req = KeyRequest.query.get_or_404(req_id)
    req.status = 'Rejected'
    req.response_time = datetime.utcnow()
    db.session.commit()
    flash('Request rejected.', 'warning')
    return redirect(url_for('admin_dashboard'))

# Admin bulk approve/reject for a file
@app.route('/admin/file/<int:file_id>/approve')
@login_required
def admin_approve_file(file_id):
    if current_user.role != 'admin':
        flash('Unauthorized Access!', 'danger')
        return redirect(url_for('index'))
    file = File.query.get_or_404(file_id)
    pending = KeyRequest.query.filter_by(file_id=file.id, status='Pending').all()
    now = datetime.utcnow()
    for r in pending:
        r.status = 'Approved'
        r.response_time = now
    db.session.commit()
    flash('All pending requests for this file approved.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/file/<int:file_id>/reject')
@login_required
def admin_reject_file(file_id):
    if current_user.role != 'admin':
        flash('Unauthorized Access!', 'danger')
        return redirect(url_for('index'))
    file = File.query.get_or_404(file_id)
    pending = KeyRequest.query.filter_by(file_id=file.id, status='Pending').all()
    now = datetime.utcnow()
    for r in pending:
        r.status = 'Rejected'
        r.response_time = now
    db.session.commit()
    flash('All pending requests for this file rejected.', 'warning')
    return redirect(url_for('admin_dashboard'))

# Initialize DB Command
@app.cli.command('initdb')
def initdb():
    db.create_all()
    print("Database initialized!")

if __name__ == '__main__':
    app.run(debug=True)
