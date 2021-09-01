from .models import *
from sqlalchemy import (event, exc)
from datetime import datetime


@event.listens_for(Tag.__table__, 'after_create')
def create_tags(*args, **kwargs):
    print('triggered')
    # courses = ['MUIC', 'ICCS205', 'ICCS206', 'ICCS309', 'ICMA106', 'ICMA213', 'ICPY101', 'ICPY102', 'ICPY105', 'ICCS101', 'ICCS121', 'ICCS161', 'ICCS204', 'ICCS225', 'ICCS227', 'ICCS311', 'ICCS312', 'ICCS370', 'ICMA216', 'ICMA223', 'ICCS208']
    course_ids = ['ICCS205', 'ICCS206', 'ICCS121', 'ICCS101', 'ICCS204']
    course_names = ['Numerical Computations', 'Discrete Mathematics', 'System Skills and Low-level Programming', 'Introduction to Computer Programming', 'Data Structures and Object-Oriented Programming']
    for course_id, course_name in zip(course_ids, course_names):
        try:
            db.session.add(Tag(course_id=course_id, name=course_name, count=0))
        except (exc.IntegrityError):
            continue
    db.session.commit()


# @event.listens_for(Users.__table__, "after_create")
# def create_fake_users(*args, **kwargs):
#     db.session.add(Users(sky_username="u6380496", display_name="Noah", encrypted_password="monkerules", mod=False, email="jksjkdjskd"))
#     db.session.commit()


# # Just to test out my functions. Don't mind these
# @event.listens_for(Thread.__table__, "after_create")
# def create_fake_threads(*args, **kwargs):
#     db.session.add(Thread(user_id=1, question="This is a question #1", body="This is a body", timestamp=datetime.now(), dupes=5))
#     db.session.add(Thread(user_id=1, question="This is a question #2", body="This is a body", timestamp=datetime.now(), dupes=3))
#     db.session.commit()


# @event.listens_for(Comment.__table__, "after_create")
# def create_fake_comments(*args, **kwargs):
#     db.session.add(Comment(user_id=1, thread_id=1, likes=3, timestamp=datetime.now(), comment_body="This is an answer #1"))
#     db.session.add(Comment(user_id=1, thread_id=2, likes=5, timestamp=datetime.now(), comment_body="This is an answer #2"))
#     db.session.commit()
