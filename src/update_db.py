from .models import *
from datetime import datetime

from .query import ReadOnly
import bcrypt

class WriteOnly:
    def __init__(self):
        self.read_queries = ReadOnly()

    def register_client(self,sky_username, display_name, password):
        passwordToByte = str.encode(password)
        hash_password = bcrypt.hashpw(passwordToByte, bcrypt.gensalt(10))
        db.session.add(Users(sky_username=sky_username, display_name=display_name, mod=False, encrypted_password=hash_password))
        db.session.commit()

    # Thread attempt begins here
    def add_thread(self, thread_title, username, thread_body, tags):
        """ Function to create a new thread """ 
       
        # Not sure if this is the way to do it
        thread = Thread(question=thread_title, body=thread_body, \
            user_id=self.read_queries.get_id_from_username(username), timestamp=datetime.now(), likes=0, dupes=1)
        db.session.add(thread)
        db.session.commit() # commit in case of one-to-many relationship foreign key
        try:
            tag_in_table = Tag.query.filter(Tag.id==1).first()
            db.session.commit()
            for tag in tags:
                tag = self.read_queries.tag_lookup(tag.split()[0])
                db.session.add(TagLine(thread_id=thread.id, tag=tag))
                tag_in_table = Tag.query.filter(Tag.id==tag).first()
                tag_in_table.count += 1
                db.session.commit()
        except:
            print("A tag doesn't exist") # we will guarantee that tag exists 
        return thread

    # If we allow threads to be deleted (probably not the way to do it)   
    def delete_thread(self, thread_id):
        thread = self.read_queries.get_thread_by_id(thread_id)
        db.session.delete(thread) # Can we do this?!
        
        db.session.commit()
    
    def edit_thread(self, thread_id, new_title, new_body):
        thread = self.read_queries.get_thread_by_id(thread_id) 

        # Even if the title or body is unchanged, it'll get "updated" with the old value
        thread.question = new_title
        thread.body = new_body

        db.session.commit()

    # combined both new_comment methods into one
    def add_comment(self, thread_id, comment_body, username, parent_id):
        parent_id = self.read_queries.get_root_comment(parent_id)
        comment = Comment(user_id=self.read_queries.get_id_from_username(username), \
            thread_id=thread_id, comment_body=comment_body, likes=0, main_comment=(parent_id is None), timestamp=datetime.now())
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

    def upvote_comment(self, comment_id, username, is_thread):
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

write_queries = WriteOnly()
