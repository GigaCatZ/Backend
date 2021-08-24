from . import db # db comes from __init__.py

class Users(db.Model):
    """DUMMY Data model for Users"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20))
    encrypted_password = db.Column(db.String(100))

class Thread(db.Model):
    """Data model for Thread"""

    __tablename__ = 'thread'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    question = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    dupes = db.Column(db.Integer)


class TagLine(db.Model):
    """Data model for Thread"""

    __tablename__ = 'tag_line'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'))
    tag = db.Column(db.String(25))


class Comment(db.Model):
    """Data model for Comments"""

    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'))
    likes = db.Column(db.Integer)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    timestamp = db.Column(db.DateTime)