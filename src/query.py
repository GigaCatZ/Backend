from .models import (Thread, db)
from .models import (Users, db)
from .models import (TagLine, db)
from .models import (Tag, db)
from datetime import datetime
import bcrypt

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

    def get_all_tags(self):
        queried = Tag.query.filter(Tag.id != 'MUIC')
        course_count = queried.count()
        course_ids = [0]*course_count
        course_names = [0]*course_count
        for idx, course in enumerate(queried):
            course_ids[idx], course_names[idx] = course.id, course.name
        return course_ids, course_names


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
