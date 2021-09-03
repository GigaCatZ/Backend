from .models import *
from datetime import datetime

from .query import ReadOnly
import bcrypt

class WriteOnly:
    def __init__(self):
        self.read_queries = ReadOnly()

    def register_client(self,sky_username, display_name, password, email):
        passwordToByte = str.encode(password)
        hash_password = bcrypt.hashpw(passwordToByte, bcrypt.gensalt(10))
        db.session.add(Users(sky_username=sky_username, display_name=display_name, mod=False, encrypted_password=hash_password, email=email))
        db.session.commit()

    def update_user(self, username, display_name, password):
        user = self.read_queries.get_user_from_username(username)
        if display_name != "": user.display_name=display_name
        if password != "":
            hash_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt(10))
            user.encrypted_password = hash_password
        db.session.commit()

    def change_user_password(self, username, new_password):
        user = self.read_queries.get_user_from_username(username)
        encrypted_password = bcrypt.hashpw(str.encode(new_password), bcrypt.gensalt(10))
        user.encrypted_password = encrypted_password
        db.session.commit()

    def change_user_modval(self, username, modval):
        user = self.read_queries.get_user_from_username(username)
        if (bool(user.mod) == modval):
            return False

        user.mod = modval
        db.session.commit()
        return True

    # Thread attempt begins here
    def add_thread(self, thread_title, username, thread_body, tags):
        """ Function to create a new thread """ 
       
        # Not sure if this is the way to do it
        thread = Thread(question=thread_title, body=thread_body, \
            user_id=self.read_queries.get_id_from_username(username), timestamp=datetime.now(), likes=0, dupes=1)
        db.session.add(thread)
        db.session.commit() # commit in case of one-to-many relationship foreign key
        
        self.add_tags_to_thread(thread.id, tags)
        return thread

    # If we allow threads to be deleted (probably not the way to do it)   
    def delete_thread(self, thread_id):
        thread = self.read_queries.get_thread_by_id(thread_id)
        db.session.delete(thread) # Can we do this?!
        
        db.session.commit()
    
    def edit_thread(self, thread_id, new_tags, new_body):
        thread = self.read_queries.get_thread_by_id(thread_id) 

        # Even if the title or body is unchanged, it'll get "updated" with the old value
        old_tags = set(self.read_queries.get_tags_from_thread(thread_id))
        tags_to_add = new_tags - old_tags
        tags_to_remove = old_tags - new_tags

        print("=============\n\n\n\n\n", tags_to_add, "\n\n", tags_to_remove, "\n\n\n\n\n==============")

        self.add_tags_to_thread(thread_id, tags_to_add)
        self.remove_tags_from_thread(thread_id, tags_to_remove)
        # tags_to_remove = 
        thread.body = new_body

        db.session.commit()

    # combined both new_comment methods into one
    def add_comment(self, thread_id, comment_body, username, parent_id):
        parent_id = self.read_queries.get_root_comment(parent_id)
        comment = Comment(user_id=self.read_queries.get_id_from_username(username), \
            thread_id=thread_id, comment_body=comment_body, likes=0, main_comment=(parent_id is None), timestamp=datetime.now(), deleted=False)
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

    def upvote_thread(self, thread_id, username):
        thread = self.read_queries.get_thread_by_id(thread_id)        
        liked_thread = self.read_queries.check_thread_like(thread_id, username)
        
        if (liked_thread is None):
            thread.likes += 1
            db.session.add(ThreadLikes(thread_id=thread_id, user_id=self.read_queries.get_id_from_username(username)))
            db.session.commit()
            return thread, True, "Successfully liked thread!"

        thread.likes -= 1
        db.session.delete(liked_thread)
        db.session.commit()
        return thread, False, "Successfully removed thread's like"

    def upvote_comment(self, comment_id, username):
        comment = self.read_queries.get_comment_by_id(comment_id)
        
        liked_comment = self.read_queries.check_comment_like(comment_id, username)
        
        if (liked_comment is None):
            comment.likes += 1
            db.session.add(CommentLikes(comment_id=comment_id, user_id=self.read_queries.get_id_from_username(username)))
            db.session.commit()
            return comment, True, "Successfully liked comment!"

        comment.likes -= 1
        db.session.delete(liked_comment)
        db.session.commit()
        return comment, False, "Successfully removed comment's like"

    def add_tag(self, course_id, course_name):
        if self.read_queries.check_tag_existence(course_id): return False
        db.session.add(Tag(course_id=course_id, name=course_name))
        db.session.commit()
        return True

    def add_tags_to_thread(self, thread_id, tags):
        for tag in tags:
            tag = self.read_queries.tag_lookup(tag.split()[0])
            db.session.add(TagLine(thread_id=thread_id, tag=tag))
            tag_in_table = Tag.query.filter(Tag.id==tag).first()
            tag_in_table.count += 1
        db.session.commit()

    def remove_tags_from_thread(self, thread_id, tags):
        for tag in tags:
            tag = self.read_queries.tag_lookup(tag.split()[0])
            db.session.delete(TagLine.query.filter(TagLine.thread_id==thread_id, TagLine.tag==tag).first())
            tag_in_table = Tag.query.filter(Tag.id==tag).first()
            tag_in_table.count -= 1
        db.session.commit()
        
    def merge_threads(self, a, b):
        thread_a = self.read_queries.get_thread_by_id(a)
        thread_b = self.read_queries.get_thread_by_id(b)
        if thread_b == None or thread_a == None: return False

        # move all extra tags in thread_b to thread_a
        additional_tags = set(self.read_queries.get_tags_from_thread(b)) - set(self.read_queries.get_tags_from_thread(a))
        self.add_tags_to_thread(a, additional_tags)

        # move comments in thread b to thread a
        for comment in self.read_queries.filter_all_comments_from_thread(b):
            comment.thread_id = a
            comment.message = "[This comment has been moved from another thread] " + comment.message
        
        # combine thread b's likes to thread a
        # likes_a = self.read_queries.users_who_liked_thread(a)
        likes_b = self.read_queries.users_who_liked_thread(b)
        for like in likes_b:
            if  self.read_queries.check_thread_like(a, self.read_queries.get_user_from_id(like.user_id).sky_username) is None:
                thread_a.likes += 1
                self.read_queries.check_thread_like(b, self.read_queries.get_user_from_id(like.user_id).sky_username).thread_id = a
               
        thread_a.dupes += thread_b.dupes
        self.delete_thread(b)
        db.session.commit()

        return True

write_queries = WriteOnly()
