from .models import *
from datetime import datetime, timedelta

from flask import jsonify
from sqlalchemy import func

class ReadOnly:
    def get_encrypted_password(self, username):
        user = self.get_user_from_username(username)
        # print('\n\n\n========== AHHHH' + user)
        return user.encrypted_password if user is not None else None

    def get_id_from_username(self, username):
        user = self.get_user_from_username(username)
        return user.id if user is not None else None

    def get_thread_by_id(self, thread_id):
        return Thread.query.filter(Thread.id == thread_id).first()

    def get_user_from_username(self, username):
        return Users.query.filter(Users.sky_username == username).first()
    
    def get_comment_by_id(self, comment_id):
        return Comment.query.filter(Comment.id == comment_id).first()

    def get_root_comment(self, parent_id):
        comment_line = CommentLine.query.filter(CommentLine.child_comment_id==parent_id).first()
        return comment_line.parent_comment_id if comment_line is not None else parent_id
    
    def get_user_from_id(self, user_id):
        return Users.query.get(int(user_id))

    def get_comment_count(self, thread_id):
        return len(Comment.query.filter(Comment.thread_id==thread_id).filter(Comment.main_comment).all())

    def get_user_from_display_name(self, display):
        return Users.query.filter(Users.display_name == display)

    def display_tags(self, queried):
        return [f'{course.course_id} | {course.name}' for course in queried]

    def display_all_tags(self):
        return self.display_tags(Tag.query)

    def display_top_tags(self):
        return self.display_tags(Tag.query.order_by(Tag.count.desc()).limit(10))
    
    def get_courseids_from_thread(self, thread_id):
        queried = TagLine.query.filter(TagLine.thread_id == thread_id).join(Tag, TagLine.tag==Tag.id).add_column(Tag.course_id).all()
        return [tag[-1] for tag in queried]
    
    def get_tag_from_id(self, tag_id):
        return Tag.query.filter(Tag.id == tag_id).first()

    def get_tags_from_thread(self, thread_id):
        queried = TagLine.query.filter(TagLine.thread_id == thread_id).join(Tag, TagLine.tag==Tag.id).all()
        tags = set()
        []
        for tag in queried:
            tag_info = self.get_tag_from_id(tag.tag)
            tags |= {f'{tag_info.course_id} | {tag_info.name}'}
        return list(tags)

    def get_thread_by_order(self, order):
        if order is not None and order in {"RECENT", "LIKES", "POPULAR", "SEARCH"}:
            queried = Thread.query.join(Users, Users.id==Thread.user_id)\
                .add_columns(Thread.id, Thread.question, Thread.timestamp, Thread.likes, Users.display_name)
            if order == "RECENT": queried = queried.order_by(Thread.timestamp.desc()).limit(10)
            elif order == "LIKES": queried = queried.order_by(Thread.likes.desc()).limit(10)
            elif order == "POPULAR": queried.filter(Thread.timestamp >= (datetime.now() - timedelta(days=31))).order_by(Thread.likes.desc()).limit(10)
            return [self.jsonify_thread(thread) for thread in queried.all()], True, "Successfully queried the threads"
        else:
            return None, False, "Not valid order"

    def check_thread_like(self, thread_id, username):
        return ThreadLikes.query.filter(ThreadLikes.thread_id==thread_id).filter(ThreadLikes.user_id==self.get_id_from_username(username)).first()

    def get_thread_like_count(self, thread_id):
        return Thread.query.filter(Thread.id==thread_id).first().likes
    
    def check_comment_like(self, comment_id, username):
        return CommentLikes.query.filter(CommentLikes.comment_id==comment_id).filter(CommentLikes.user_id==self.get_id_from_username(username)).first()

    def get_comment_like_count(self, comment_id):
        return Comment.query.filter(Comment.id==comment_id).first().likes
    
    def jsonify_thread(self, thread):
        _, thread_id, title, date, likes, display_name = thread
        return {'thread_id':thread_id, 'title':title, 'likes':likes, 'display_name':display_name, 'date':date, \
            'tags':self.get_courseids_from_thread(thread_id), 'comment_count': self.get_comment_count(thread_id)}

    def tag_lookup(self, course_id):
        tag = Tag.query.filter(Tag.course_id == course_id).first()
        return tag.id if tag is not None else None

    def get_top_comment(self, thread_id):
        return Comment.query.filter(Comment.thread_id == thread_id).order_by(Comment.likes.desc()).first()

    def get_thread_by_dupe(self):
        return Thread.query.filter(Thread.dupes > 1).order_by(Thread.dupes.desc()).limit(5)

    def get_comments_of_thread(self, thread_id):
        queried = Comment.query.filter(Comment.thread_id == thread_id).filter(Comment.main_comment).order_by(Comment.likes.desc()).all()
        return [{'sender': self.get_user_from_id(comment.user_id).display_name, 'timestamp': comment.timestamp, 'body': comment.comment_body, \
            'likes' : comment.likes, 'replies' : self.get_all_replies(comment.id), 'comment_id' : comment.id , 'reply' : False} for comment in queried]

    def get_all_replies(self, parent_id):
        queried = Comment.query.join(CommentLine, CommentLine.child_comment_id==Comment.id).filter(CommentLine.parent_comment_id == parent_id).all()
        return [{'sender': self.get_user_from_id(comment.user_id).display_name, 'timestamp': comment.timestamp, 'body': comment.comment_body, \
            'likes' : comment.likes, 'comment_id' : comment.id , 'reply' : False } for comment in queried]

    def get_all_tags(self):
        return Tag.query.all()

read_queries = ReadOnly()
