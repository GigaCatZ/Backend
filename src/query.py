from .models import (Thread, db)
from .models import (Users, db)
from datetime import datetime
import bcrypt

class ReadOnly:
    def get_encrypted_password(self, username):
        user = Users.query.filter(Users.username == username)
        # print('\n\n\n========== AHHHH' + user)
        return user.first().encrypted_password if user is not None and user.first() is not None else None

class WriteOnly:
    def register_client(self,sky_username, username, password, email) -> None:
        passwordToByte = str.encode(password)
        hash_password = bcrypt.hashpw(passwordToByte, bcrypt.gensalt(10)) 
        # new_user = Users(sky_username,username,hash_password,email)
        test = Users()
        test.sky_username = sky_username
        test.username = username
        test.encrypted_password = hash_password
        test.email = email
        db.session.add(test)
        db.session.commit()

    # Thread attempt begins here
    def add_thread(self, thread_title, user_id, thread_body):
        """ Function to create a new thread """ 
        thread = Thread()
        thread.question = thread_title
        thread.body = thread_body
        thread.user_id = user_id # Is this supposed to be an integer or a string / userid or SKY id ?!?!??!
        thread.timestamp = datetime.now() # Not sure if this is necessary since Pornkamol said she would handle it in DB
       
        # Not sure if this is the way to do it
        db.session.add(thread)
        db.session.commit()
       
    # If we allow threads to be deleted (probably not the way to do it)   
    def delete_thread(self, thread_id):
        thread = Thread.query.filter(Thread.id == thread_id)
        db.session.delete(thread) # Can we do this?!
        db.session.commit()
    
    def edit_thread(self, thread_id, new_title, new_body):
        thread = Thread.query.filter(Thread.id == thread_id)

        # Even if the title or body is unchanged, it'll get "updated" with the old value
        thread.question = new_title
        thread.body = new_body
        db.session.commit()
    


read_queries = ReadOnly()
write_queries = WriteOnly()
