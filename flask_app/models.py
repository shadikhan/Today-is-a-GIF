from datetime import datetime
from flask_app import db, login_manager
from flask_login import UserMixin

import pyotp
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    lastUpdated = db.Column(db.DateTime, nullable=False, default=datetime.now)

    interest1 = db.Column(db.String(60), nullable=False)
    interest2 = db.Column(db.String(60), nullable=False)
    interest3 = db.Column(db.String(60), nullable=False)

    otp_secret = db.Column(db.String(16), nullable=False)

    GIFs = db.relationship("UserGIF", backref="user", lazy=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.otp_secret = base64.b32encode(os.urandom(10)).decode()
        self.otp_secret = pyotp.random_base32()
    
    def get_auth_uri(self):
        servicer = 'CMSC388J-2FA'

        return ('otpauth://totp/{0}:{1}?secret={2}&issuer={0}'.format(
            servicer, self.username, self.otp_secret
        ))
    
    def verify_totp(self, token):
        totp_client = pyotp.TOTP(self.otp_secret)
        return totp_client.verify(token)

class UserGIF(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    

class GIFPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    link = db.Column(db.Text, nullable=False)


