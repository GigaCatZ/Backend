from . import db # db comes from __init__.py
from flask_login import UserMixin

class Users(UserMixin, db.Model):
    """DUMMY Data model for Users"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sky_username = db.Column(db.String(20), nullable=False, unique=True)
    display_name = db.Column(db.String(20), nullable=False, unique=True)
    encrypted_password = db.Column(db.String(100), nullable=False)
    mod = db.Column(db.Boolean, default=False)

    

class Thread(db.Model):
    """Data model for Thread"""

    __tablename__ = 'thread'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=True) # This is new (nullable=True because body can be empty?)
    timestamp = db.Column(db.DateTime, nullable=False)
    dupes = db.Column(db.Integer, default=1)
    likes = db.Column(db.Integer, default=0)


class TagLine(db.Model):
    """Data model for TagLine"""

    __tablename__ = 'tag_line'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), nullable=False)
    tag = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)


class Tag(db.Model):
    """Data model for Tags"""

    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.String(25))
    name = db.Column(db.String(100))
    count = db.Column(db.Integer, default=0)


class Comment(db.Model):
    """Data model for Comments"""

    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), nullable=False)
    comment_body = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    timestamp = db.Column(db.DateTime)
    
    # A list of subcomments, not sure if this is gonna work
    subcomments = []
