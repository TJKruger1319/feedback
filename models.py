from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):

    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    @classmethod
    def register(cls, username, pwd, email, first, last):
        """Register user with hashed password"""
        hash = bcrypt.generate_password_hash(pwd)
        hash_utf8 = hash.decode("utf8")

        return cls(username=username, password=hash_utf8, email=email, first_name=first, last_name=last)
    
    @classmethod
    def authenticate(cls, user, pwd):
       """Check to see if user and password pair in database"""
       user = User.query.filter_by(username=user).first()

       if user and bcrypt.check_password_hash(user.password, pwd):
           return user
       else:
           return False
       
class Feedback(db.Model):

    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True, auto_increment=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, db.ForeignKey("users.username"))
