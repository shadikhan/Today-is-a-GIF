from datetime import datetime
from flask_app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    
    GIFs = db.relationship("UserGIFs", backref="user", lazy=True)

class UserGIFs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lastUpdated = db.Column(db.DateTime, nullable=False, default=datetime.now)
    link = db.Column(db.Text, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class GIFPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    link = db.Column(db.Text, nullable=False)


