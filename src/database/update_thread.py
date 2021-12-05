from datetime import datetime

from flask_login import current_user

from .models import *
from .query import ReadOnly


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
        db.session.commit()  # commit in case of one-to-many relationship foreign key

        self.add_tags_to_thread(thread.id, set(tags) - {None})
        return thread

    def remove_tag_count(self, tags):
        for tag in tags:
            tag = self.read_queries.get_tag_from_courseid(tag.split(' | ')[0])
            tag.count -= 1

    # If we allow threads to be deleted (probably not the way to do it)   
    def delete_thread(self, thread_id):
        thread = self.read_queries.get_thread_by_id(thread_id)
        self.remove_tag_count(self.read_queries.get_tags_from_thread(thread_id))
        db.session.delete(thread)  # Can we do this?!
        db.session.commit()

    def edit_thread(self, thread_id, new_tags, new_body):
        thread = self.read_queries.get_thread_by_id(thread_id)

        # Even if the title or body is unchanged, it'll get "updated" with the old value
        old_tags = set(self.read_queries.get_tags_from_thread(thread_id))
        tags_to_add = new_tags - old_tags - {None}
        tags_to_remove = old_tags - new_tags - {None}

        self.add_tags_to_thread(thread_id, tags_to_add)
        self.remove_tags_from_thread(thread_id, tags_to_remove)
        # tags_to_remove = 
        thread.body = new_body
        db.session.commit()

    def upvote_thread(self, thread_id):
        thread = self.read_queries.get_thread_by_id(thread_id)
        liked_thread = self.read_queries.check_thread_like(thread_id)

        if liked_thread is None:
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
            if tag is not None:
                db.session.add(TagLine(thread_id=thread_id, tag=tag))
                tag_in_table = Tag.query.filter(Tag.id == tag).first()
                tag_in_table.count += 1
            db.session.commit()

    def remove_tags_from_thread(self, thread_id, tags):
        for tag in tags:
            tag = self.read_queries.tag_lookup(tag.split()[0])
            if tag is not None:
                db.session.delete(TagLine.query.filter(TagLine.thread_id == thread_id, TagLine.tag == tag).first())
                tag_in_table = Tag.query.filter(Tag.id == tag).first()
                tag_in_table.count -= 1
            db.session.commit()

    def merge_threads(self, a, b):
        thread_a = self.read_queries.get_thread_by_id(a)
        thread_b = self.read_queries.get_thread_by_id(b)
        if thread_b is None or thread_a == None: return False

        tags_a = set(self.read_queries.get_tags_from_thread(a))
        tags_b = set(self.read_queries.get_tags_from_thread(b))

        for tag in tags_a & tags_b:
            stag = self.read_queries.get_tag_from_courseid(tag.split(' | ')[0])
            tag.count -= 1

        # move all extra tags in thread_b to thread_a and decrement count if intersect
        self.remove_tag_count(tags_a & tags_b)
        self.add_tags_to_thread(a, tags_b - tags_a)

        # move comments in thread b to thread a
        for comment in self.read_queries.filter_all_comments_from_thread(b):
            comment.thread_id = a
            # this is currently not working atm (need to find a way to display new line)
            # if not comment.deleted:
            #     comment.comment_body = "[This comment has been moved from another thread] \n" + comment.comment_body

        # combine thread b's likes to thread a
        # likes_a = self.read_queries.users_who_liked_thread(a)
        likes_b = self.read_queries.users_who_liked_thread(b)
        for like in likes_b:
            if self.read_queries.check_manual_thread_like(a, like.user_id) is None:
                thread_a.likes += 1
                self.read_queries.check_manual_thread_like(b, like.user_id).thread_id = a

        thread_a.dupes += thread_b.dupes
        self.delete_thread(b)
        db.session.commit()

        return True
