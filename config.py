import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    # Use SQLite instead of MySQL
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'dual_access_cloud.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB upload limit
