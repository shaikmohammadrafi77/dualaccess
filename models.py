from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    attributes = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_active(self):
        return True

    def __repr__(self):
        return f"<User {self.username}>"

class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    access_policy = db.Column(db.String(200))
    encrypted_path = db.Column(db.String(300))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime)

    owner = db.relationship('User', backref='files')

    def __repr__(self):
        return f"<File {self.filename}>"

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    request_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50))
    attempt_type = db.Column(db.String(50))

    user = db.relationship('User', backref='transactions')
    file = db.relationship('File', backref='transactions')

class KeyRequest(db.Model):
    __tablename__ = 'key_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    status = db.Column(db.String(50), default="Pending")
    request_time = db.Column(db.DateTime, default=datetime.utcnow)
    response_time = db.Column(db.DateTime)

    user = db.relationship('User', backref='key_requests')
    file = db.relationship('File', backref='key_requests')
