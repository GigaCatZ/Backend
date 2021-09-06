from .models import *
from .query import ReadOnly

from flask_login import current_user

from datetime import datetime

class UpdateThread:
    def __init__(self):
        self.read_queries = ReadOnly()

        # Thread attempt begins here
    def add_thread(self, thread_title, thread_body, tags):
        """ Function to create a new thread """ 
       
        # Not sure if this is the way to do it
        thread = Thread(question=thread_title, body=thread_body, \
            user_id=current_user.id, timestamp=datetime.now(), likes=0, dupes=1)
        db.session.add(thread)
        db.session.commit() # commit in case of one-to-many relationship foreign key
        
        self.add_tags_to_thread(thread.id, tags)
        return thread

    # If we allow threads to be deleted (probably not the way to do it)   
    def delete_thread(self, thread_id):
        thread = self.read_queries.get_thread_by_id(thread_id)
        for tag in self.read_queries.get_tags_from_thread(thread_id):
            tag = self.read_queries.get_tag_from_courseid(tag.split(' | ')[0])
            tag.count -= 1
        db.session.delete(thread) # Can we do this?!
        
        db.session.commit()
    
    def edit_thread(self, thread_id, new_tags, new_body):
        thread = self.read_queries.get_thread_by_id(thread_id) 

        # Even if the title or body is unchanged, it'll get "updated" with the old value
        old_tags = set(self.read_queries.get_tags_from_thread(thread_id))
        tags_to_add = new_tags - old_tags
        tags_to_remove = old_tags - new_tags

        self.add_tags_to_thread(thread_id, tags_to_add)
        self.remove_tags_from_thread(thread_id, tags_to_remove)
        # tags_to_remove = 
        thread.body = new_body

        db.session.commit()
        
    def upvote_thread(self, thread_id):
        thread = self.read_queries.get_thread_by_id(thread_id)        
        liked_thread = self.read_queries.check_thread_like(thread_id)
        
        if (liked_thread is None):
            thread.likes += 1
            db.session.add(ThreadLikes(thread_id=thread_id, user_id=current_user.id))
            db.session.commit()
            return thread, True, "Successfully liked thread!"

        thread.likes -= 1
        db.session.delete(liked_thread)
        db.session.commit()
        return thread, False, "Successfully removed thread's like"

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
            if not comment.deleted:
                comment.comment_body = "[This comment has been moved from another thread] \n" + comment.comment_body
        
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
