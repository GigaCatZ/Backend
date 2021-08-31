from .models import (Thread, db)
from .models import (Users, db)
from .models import (Comment, db)
from .models import (TagLine, db)
from .models import (Tag, db)
from datetime import datetime

from .query import ReadOnly

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
    
    def new_comment(self, thread_id, comment_body, username):
        comment = Comment(user_id=username, thread_id=thread_id, comment_body=comment_body, timestamp=datetime.now())
        db.session.add(comment)
        db.session.commit()

    def new_comment_reply(self, thread_id, parent_comment_id, comment_body, username):
        comment = Comment(user_id=username, thread_id=thread_id, comment_body=comment_body, timestamp=datetime.now())

        # Not sure if I should also add this individual comment to the db.session but, we'll see!?
        parent_comment = self.read_queries.get_comment_by_id(parent_comment_id)
        parent_comment.subcomments.append(comment)
        db.session.commit()    

    def edit_comment(self, comment_id, new_comment_body):
        comment = self.read_queries.get_comment_by_id(comment_id)
        comment.comment_body = new_comment_body

        db.session.commit()

    def delete_comment(self, comment_id):
        comment = self.read_queries.get_comment_by_id(comment_id)

        # Would be nice if frontend could make this italic or something
        comment.comment_body = "This comment has been removed by the user."
        db.session.commit()

    def upvote_thread(self, thread_id):
        thread = self.read_queries.get_thread_by_id(thread_id)
        thread.likes += 1
        db.session.commit()
    
read_queries = ReadOnly()
write_queries = WriteOnly()
