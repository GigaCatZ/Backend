from .models import *
from datetime import datetime, timedelta

from flask_login import current_user

from .query import ReadTag

def get_readable_day(timestamp):
    return timestamp.strftime('%a, %d %b %Y %H:%M:%S GMT+07:00')

class ReadThread:
    def __init__(self):
        self.read_tag = ReadTag()

    def get_thread_by_id(self, thread_id):
        return Thread.query.filter(Thread.id == thread_id).first()

    def get_comment_count(self, thread_id):
        return len(Comment.query.filter(Comment.thread_id==thread_id).filter(Comment.main_comment).all())
    
    def get_courseids_from_thread(self, thread_id):
        queried = TagLine.query.filter(TagLine.thread_id == thread_id).join(Tag, TagLine.tag==Tag.id).add_column(Tag.course_id).all()
        return [tag[-1] for tag in queried]
    
    def get_tags_from_thread(self, thread_id):
        queried = TagLine.query.filter(TagLine.thread_id == thread_id).join(Tag, TagLine.tag==Tag.id).all()
        tags = list()
        for tag in queried:
            tag_info = self.read_tag.get_tag_from_id(tag.tag)
            tags.append(f'{tag_info.course_id} | {tag_info.name}')
        return tags

    def get_thread_by_order(self, order):
        if order is not None and order in {"RECENT", "LIKES", "POPULAR", "SEARCH"}:
            queried = Thread.query.join(Users, Users.id==Thread.user_id)\
                .add_columns(Thread.id, Thread.question, Thread.timestamp, Thread.likes, Users.display_name)
            if order == "RECENT": queried = queried.order_by(Thread.timestamp.desc()).limit(10)
            elif order == "LIKES": queried = queried.order_by(Thread.likes.desc()).limit(10)
            elif order == "POPULAR": queried = queried.filter(Thread.timestamp >= (datetime.now() - timedelta(days=31))).order_by(Thread.likes.desc(), Thread.dupes.desc()).limit(10)
            else: queried = queried.order_by(Thread.likes.desc(), Thread.dupes.desc(), Thread.timestamp.desc())
            return [self.jsonify_thread(thread) for thread in queried.all()], True, "Successfully queried the threads"
        else:
            return None, False, "Not valid order"
    
    def check_thread_like(self, thread_id):
        if not current_user.is_authenticated: return None
        return ThreadLikes.query.filter(ThreadLikes.thread_id==thread_id).filter(ThreadLikes.user_id==current_user.id).first()

    def get_thread_like_count(self, thread_id):
        return Thread.query.filter(Thread.id==thread_id).first().likes
    
    def jsonify_thread(self, thread):
        _, thread_id, title, date, likes, display_name = thread
        return {'thread_id':thread_id, 'title':title, 'likes':likes, 'display_name':display_name, 'date': get_readable_day(date) , \
            'tags':self.get_courseids_from_thread(thread_id), 'comment_count': self.get_comment_count(thread_id), 'reported_as_dupes' : [] }
            # TODO: edit reported_as_dupes when we implement report dupes feature
    
    def get_top_comment(self, thread_id):
        # Nawat, if you're reading this, filtering by Comment.main_comment was added at the request of PK since this function could return the most upvoted subcomment
        return Comment.query.filter(Comment.thread_id == thread_id).filter(Comment.main_comment).order_by(Comment.likes.desc()).first()
    
    def get_thread_by_dupe(self):
        return Thread.query.filter(Thread.dupes > 1).order_by(Thread.dupes.desc()).limit(5)
    
    def filter_all_comments_from_thread(self, thread_id):
        return Comment.query.filter(Comment.thread_id == thread_id).all()

    def users_who_liked_thread(self, thread_id):
        return ThreadLikes.query.filter(ThreadLikes.thread_id==thread_id).all()
