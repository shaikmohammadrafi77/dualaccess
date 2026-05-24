import os
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, File, KeyRequest

def seed():
    with app.app_context():
        db.create_all()

        # Ensure uploads folder and sample file exist
        uploads_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(uploads_dir, exist_ok=True)
        sample_path = os.path.join(uploads_dir, 'sample.txt')
        if not os.path.exists(sample_path):
            with open(sample_path, 'w', encoding='utf-8') as f:
                f.write('This is a sample file for demo purposes.')

        users_data = [
            ('owner1', 'password', 'owner', 'manager,finance'),
            ('enduser1', 'password', 'enduser', 'employee,hr'),
            ('authority1', 'password', 'authority', 'admin,keys'),
            ('admin1', 'password', 'admin', 'superadmin'),
        ]

        existing_usernames = {u.username for u in User.query.all()}
        for username, pwd, role, attrs in users_data:
            if username not in existing_usernames:
                db.session.add(
                    User(
                        username=username,
                        password=generate_password_hash(pwd),
                        role=role,
                        attributes=attrs,
                    )
                )
        db.session.commit()

        owner = User.query.filter_by(username='owner1').first()
        if owner and not File.query.filter_by(filename='sample.txt', owner_id=owner.id).first():
            db.session.add(
                File(
                    filename='sample.txt',
                    owner_id=owner.id,
                    access_policy='role:enduser',
                    encrypted_path=sample_path,
                )
            )
            db.session.commit()

        # Seed authority key requests if empty
        if KeyRequest.query.count() == 0:
            enduser = User.query.filter_by(username='enduser1').first()
            sample = File.query.filter_by(filename='sample.txt', owner_id=owner.id).first() if owner else None
            if enduser and sample:
                db.session.add(KeyRequest(user_id=enduser.id, file_id=sample.id, status='Pending'))
                db.session.commit()

        print('Database initialized with demo data!')

if __name__ == '__main__':
    seed()
