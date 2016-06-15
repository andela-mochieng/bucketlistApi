"""Bucketlist models """
from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from config import config
from sqlalchemy import UniqueConstraint


class BucketListItem(db.Model):
    """Define items in a user's bucketlist."""

    __tablename__ = "bucketlistitems"
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(256), unique=True)
    item_description = db.Column(db.String(256), unique=True)
    done = db.Column(db.Boolean(), default=False, index=True)
    date_created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    bucketlist_id = db.Column(db.Integer, db.ForeignKey(
        'bucketlists.id'), nullable=False)

    def __init__(self, item_name, item_description, bucketlist_id, done=False):
        """Method used for instantiation of a BucketListItem Model"""
        self.item_name = item_name
        self.item_description = item_description
        self.bucketlist_id = bucketlist_id

    def __repr__(self):
        """Return a string representation of the user."""
        return '{}'.format(self.id)



class BucketList(db.Model):
    """
    Define a bucketlist.
    """

    __tablename__ = 'bucketlists'
    __table_args__ = (UniqueConstraint('list_name', 'created_by'),)
    id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(100))

    bucketlist_items = db.relationship(
        'BucketListItem', backref='bucketlist', lazy='dynamic')
    created_by = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())

    def __repr__(self):
        """Return a string representation of the bucketlist."""
        return '<BucketList %r>' % self.id



class User(db.Model):
    """
    Define a user.
    Attributes:
        id (int): A user's id.
        username (str): A unique identifier for a user.
        bucketlists (relationship): User's bucketlists.
    """

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(128))
    date_created = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    bucketlists = db.relationship(
        'BucketList', backref='bucketlist_', lazy='dynamic')

    def __init__(self, username, password):
        """Initialize a user object."""
        self.username = username
        self.password_hash = generate_password_hash(str(password))

    def verify_password(self, password):
        """
        Verify a user's password.
        Args:
            password
        Returns:
            bool: True if the hash value of password mathes a user's
            stored password hash.
        """
        return check_password_hash(self.password_hash, str(password))

    @property
    def password(self):
        """User password."""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Generate and save a hash of <password>."""
        self.password_hash = generate_password_hash(password)

    def generate_auth_token(self, expiration=10000):
        """
        Generate a token expiring after 10 minutes.
        Returns:
            token: authentication token
        """
        token_serializer = Serializer(config['SECRET_KEY'],
                                      expires_in=expiration)
        return token_serializer.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        """
        Verifies tokens
        Args:
            token: The token to be verified
        Returns:
            The user whose id is in the decoded token
        """
        token_serializer = Serializer(config['SECRET_KEY'])
        try:
            data = token_serializer.loads(token)
        except (SignatureExpired, BadSignature):
            return {'error': 'The token is invalid'}
        user = User.query.get(data['id'])

        return user



    def __repr__(self):
        """Return a string representation of the user."""
        return '<User %r>' % self.username


    def get(self):
        return {
            'id': self.id,
            'username': self.username,
            'date_created': str(self.date_created)
        }
