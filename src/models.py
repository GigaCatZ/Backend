from . import db # db comes from __init__.py

class Users(db.Model):
    """DUMMY Data model for Users"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(20), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    encrypted_password = db.Column(db.String(100), nullable=False)
    mod = db.Column(db.Boolean, nullable=False)
    

class Thread(db.Model):
    """Data model for Thread"""

    __tablename__ = 'thread'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    dupes = db.Column(db.Integer, default=1)


class TagLine(db.Model):
    """Data model for Thread"""

    __tablename__ = 'tag_line'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), nullable=False)
    tag = db.Column(db.String(25))


class Comment(db.Model):
    """Data model for Comments"""

    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), nullable=False)
    likes = db.Column(db.Integer, default=0)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    timestamp = db.Column(db.DateTime)