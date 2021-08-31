from .models import (Thread, db)
from .models import (Users, db)
from .models import (TagLine, db)
from .models import (Tag, db)
from .models import (Comment, db)
from datetime import datetime

import bcrypt
from flask import jsonify

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
    
    def get_user_from_id(self, user_id):
        return Users.query.get(int(user_id))

    def get_user_from_display_name(self, display):
        return Users.query.filter(Users.display_name == display)

    def display_tags(self, queried):
        return [f'{course.course_id} | {course.name}' for course in queried]

    def display_all_tags(self):
        return self.display_tags(Tag.query.filter(Tag.id != 1))

    def display_top_tags(self):
        return self.display_tags(Tag.query.filter(Tag.id != 1).order_by(Tag.count.desc()).limit(10))
    
    def get_courseids_from_thread(self, thread_id):
        queried = TagLine.query.filter(TagLine.thread_id == thread_id).join(Tag, TagLine.tag==Tag.id).add_column(Tag.course_id).all()
        return [tag[-1] for tag in queried]
    
    def get_tag_from_id(self, tag_id):
        return Tag.query.filter(Tag.id == tag_id).first()

    def get_tags_from_thread(self, thread_id):
        queried = TagLine.query.filter(TagLine.tag != 1).filter(TagLine.thread_id == thread_id).join(Tag, TagLine.tag==Tag.id).all()
        tags = set()
        for tag in queried:
            tag_info = self.get_tag_from_id(tag.id)
            tags |= {f'{tag_info.course_id} | {tag_info.name}'}
        return list(tags)

    def get_thread_by_order(self, order):
        if order is not None and order == "RECENT":
            queried = Thread.query.join(Users, Users.id==Thread.user_id)\
                .add_columns(Thread.id, Thread.question, Thread.timestamp, Thread.likes, Users.display_name)\
                    .order_by(Thread.timestamp.desc()).limit(10)
            return [self.jsonify_thread(thread) for thread in queried.all()], "Successfully queried tags and threads"
        else:
            return None, "Not valid order"

    def jsonify_thread(self, thread):
        _, thread_id, title, date, likes, display_name = thread
        # print('\n\n\n\n', thread_id, title, date, display_name, '\n\n\n\n')
        return {'thread_id':thread_id, 'title':title, 'likes':likes, 'display_name':display_name, 'date':date, 'tags':self.get_courseids_from_thread(thread_id)}

    def tag_lookup(self, course_id):
        tag = Tag.query.filter(Tag.course_id == course_id).first()
        return tag.id if tag is not None else None

    def get_top_comment(self, thread_id):
        return Comment.query.filter(Comment.thread_id == thread_id).order_by(Comment.likes.desc()).first()

    def get_thread_by_dupe(self):
        return Thread.query.filter(Thread.dupes > 1).order_by(Thread.dupes.desc()).limit(5)


read_queries = ReadOnly()