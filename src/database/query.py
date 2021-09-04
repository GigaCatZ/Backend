from .models import *
from datetime import datetime, timedelta

from flask import jsonify
from flask_login import current_user

# don't change the order or there will be weird circular imports error
from .query_tag import ReadTag
from .query_thread import ReadThread, get_readable_day

class ReadUsers:
    def get_encrypted_password(self, username):
        user = self.get_user_from_username(username)
        return user.encrypted_password if user is not None else None
    
    def get_user_from_username(self, username):
        return Users.query.filter(Users.sky_username == username).first()
    
    def get_user_from_id(self, user_id):
        return Users.query.get(int(user_id))
    
    def get_user_from_display_name(self, display):
        return Users.query.filter(Users.display_name == display)

    def get_users(self):
        queried = Users.query.all()
        return [{'sky_username' : user.sky_username, 'display_name' : user.display_name, 'mod' : user.mod, 'email' : user.email} for user in queried]

class ReadComment:
    def __init__(self):
        self.read_users = ReadUsers()

    def get_comment_by_id(self, comment_id):
        return Comment.query.filter(Comment.id == comment_id).first()
    
    def get_root_comment(self, parent_id):
        comment_line = CommentLine.query.filter(CommentLine.child_comment_id==parent_id).first()
        return comment_line.parent_comment_id if comment_line is not None else parent_id

    def check_comment_like(self, comment_id):
        if not current_user.is_authenticated: return None
        return CommentLikes.query.filter(CommentLikes.comment_id==comment_id).filter(CommentLikes.user_id==current_user.id).first()

    def get_comment_like_count(self, comment_id):
        return Comment.query.filter(Comment.id==comment_id).first().likes

    def get_comments_of_thread(self, thread_id):
        queried = Comment.query.filter(Comment.thread_id == thread_id).filter(Comment.main_comment).order_by(Comment.likes.desc()).all()
        return [{'sender': self.read_users.get_user_from_id(comment.user_id).display_name, 'timestamp': get_readable_day(comment.timestamp), 'body': comment.comment_body, 'is_liked': self.check_comment_like(comment.id) is not None, \
                'likes' : comment.likes, 'replies' : self.get_all_replies(comment.id), 'comment_id' : comment.id , 'reply' : False, 'deleted' : comment.deleted} for comment in queried]

    def get_all_replies(self, parent_id):
        queried = Comment.query.join(CommentLine, CommentLine.child_comment_id==Comment.id).filter(CommentLine.parent_comment_id == parent_id).all()
        return [{'sender': self.read_users.get_user_from_id(comment.user_id).display_name, 'timestamp':get_readable_day(comment.timestamp), 'body': comment.comment_body, \
                'is_liked' : self.check_comment_like(comment.id) is not None, 'likes' : comment.likes, 'comment_id' : comment.id , 'reply' : False, 'deleted' : comment.deleted } for comment in queried]

class ReadOnly(ReadUsers, ReadThread, ReadComment, ReadTag):
    pass

read_queries = ReadOnly()