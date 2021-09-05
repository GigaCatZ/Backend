from .models import *
from datetime import datetime

from flask_login import current_user

from .query import ReadOnly
from .update_thread import UpdateThread
import bcrypt

from ..features.email import emailer

class UpdateUsers:
    def __init__(self):
        self.read_queries = ReadOnly()
    
    def register_client(self,sky_username, display_name, password, email):

        passwordToByte = str.encode(password)
        hash_password = bcrypt.hashpw(passwordToByte, bcrypt.gensalt(10))
        db.session.add(Users(sky_username=sky_username, display_name=display_name, mod=False, encrypted_password=hash_password, email=email))
        db.session.commit()
    
    def update_user(self, display_name, password):
        user = self.read_queries.get_user_from_id(current_user.id)
        if display_name != "" and user.display_name != display_name: 
            user.display_name=display_name
        if password != "":
            hash_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt(10))
            user.encrypted_password = hash_password
            emailer.user_changed_password(current_user.email, current_user.sky_username)
        db.session.commit()

    def change_user_password(self, username, new_password):
        user = self.read_queries.get_user_from_username(username)
        encrypted_password = bcrypt.hashpw(str.encode(new_password), bcrypt.gensalt(10))
        user.encrypted_password = encrypted_password
        db.session.commit()
        emailer.we_changed_users_password(user.email, username, new_password)

    def change_user_modval(self, username, modval):
        user = self.read_queries.get_user_from_username(username)
        if (bool(user.mod) == modval):
            return False

        user.mod = modval
        if modval == True: emailer.notify_new_moderators(user.email, username)
        db.session.commit()
        return True

class UpdateComment:
    def __init__(self):
        self.read_queries = ReadOnly()

    # combined both new_comment methods into one
    def add_comment(self, thread_id, comment_body, parent_id):
        parent_id = self.read_queries.get_root_comment(parent_id)
        comment = Comment(user_id=current_user.id, thread_id=thread_id, comment_body=comment_body, likes=0, \
            main_comment=(parent_id is None), timestamp=datetime.now(), deleted=False)
        db.session.add(comment)
        db.session.commit()
        if not comment.main_comment:
            db.session.add(CommentLine(parent_comment_id=parent_id, child_comment_id=comment.id))
            db.session.commit()
        return comment.id

    def edit_comment(self, comment_id, new_comment_body):
        comment = self.read_queries.get_comment_by_id(comment_id)
        comment.comment_body = new_comment_body

        db.session.commit()

    def delete_comment(self, comment_id):
        comment = self.read_queries.get_comment_by_id(comment_id)
        # Sayonara da
        comment.deleted=True
        # Would be nice if frontend could make this italic or something
        comment.comment_body = "This comment has been removed by the user."
        db.session.commit()

    def upvote_comment(self, comment_id):
        comment = self.read_queries.get_comment_by_id(comment_id)
        liked_comment = self.read_queries.check_comment_like(comment_id)
    
        if (liked_comment is None):
            comment.likes += 1
            db.session.add(CommentLikes(comment_id=comment_id, user_id=current_user.id))
            db.session.commit()
            return comment, True, "Successfully liked comment!"

        comment.likes -= 1
        db.session.delete(liked_comment)
        db.session.commit()
        return comment, False, "Successfully removed comment's like"


class WriteOnly(UpdateUsers, UpdateComment, UpdateThread):
    def add_tag(self, course_id, course_name):
        if self.read_queries.check_tag_existence(course_id): return False
        db.session.add(Tag(course_id=course_id, name=course_name))
        db.session.commit()
        return True


write_queries = WriteOnly()