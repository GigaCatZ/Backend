from .models import (Thread, db)
from .models import (Users, db)
from .models import (TagLine, db)
from .models import (Tag, db)
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
        return Thread.query.filter(Thread.id == thread_id)

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

    def get_tags_from_thread(self, thread_id):
        queried = TagLine.query.filter(TagLine.thread_id == thread_id).all()
        return [tag.id for tag in queried]
    
    def get_thread_by_order(self, order):
        if order is not None and order == "RECENT":
            queried = Thread.query.join(Users, Users.id==Thread.user_id)\
                .add_columns(Thread.id, Thread.question, Thread.timestamp, Users.display_name)\
                    .order_by(Thread.timestamp.desc()).limit(10)
            print("=======\n\n\n", queried.all(), "\n\n\n=======")
            return [self.jsonify_thread(thread) for thread in queried.all()], "Successfully queried tags and threads"
        else:
            return None, "Not valid order"

    def jsonify_thread(self, thread):
        _, thread_id, title, date, display_name = thread
        # print('\n\n\n\n', thread_id, title, date, display_name, '\n\n\n\n')
        return {'thread_id':thread_id, 'title':title, 'display_name':display_name, 'date':date, 'tags':self.get_tags_from_thread(thread_id)}

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
            tag_in_table = Tag.query.filter(Tag.id=='MUIC').first()
            db.session.commit()
            for tag in tags:
                tag = tag.split()[0]
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
    
read_queries = ReadOnly()
write_queries = WriteOnly()
