from .models import (Thread, Comment, Tag, db)
from sqlalchemy import (event, exc)


@event.listens_for(Tag.__table__, 'after_create')
def create_tags(*args, **kwargs):
    print('triggered')
    # courses = ['MUIC', 'ICCS205', 'ICCS206', 'ICCS309', 'ICMA106', 'ICMA213', 'ICPY101', 'ICPY102', 'ICPY105', 'ICCS101', 'ICCS121', 'ICCS161', 'ICCS204', 'ICCS225', 'ICCS227', 'ICCS311', 'ICCS312', 'ICCS370', 'ICMA216', 'ICMA223', 'ICCS208']
    course_ids = ['MUIC', 'ICCS205', 'ICCS206', 'ICCS121', 'ICCS101', 'ICCS204']
    course_names = ['MUIC', 'Numerical Computations', 'Discrete Mathematics', 'System Skills and Low-level Programming', 'Introduction to Computer Programming', 'Data Structures and Object-Oriented Programming']
    for course_id, course_name in zip(course_ids, course_names):
        try:
            db.session.add(Tag(course_id=course_id, name=course_name, count=0))
        except (exc.IntegrityError):
            continue
    db.session.commit()


# Just to test out my functions. Don't mind these
@event.listens_for(Thread.__table__, 'after_create')
def create_threads(*args, **kwargs):
    print("I hate my life")
    thread_user = [num for num in range(6380490, 6380500)]
    questions = [f"This is question #{n}" for n in range(10)]
    timestamps = ["2021-09-09 02:30:00" for _ in range(10)]
    duplicates = [1, 1, 1, 1, 1, 6, 5, 4, 3, 2]
    likeys = [0 for _ in range(10)]
    for user, title, time, dupe, like in zip(thread_user, questions, timestamps, duplicates, likeys):
        try:
            db.session.add(Thread(user_id=user, question=title, timestamp=time, dupes=dupe, likes=like))
        except exc.IntegrityError:
            print("error")
            continue
    db.session.commit()


@event.listens_for(Comment.__table__, "after_create")
def create_fake_comments(*args, **kwargs):
    print("I hate my life the sequel")
    users = [num for num in range(6380490, 6380500)]
    thread_ids = [1 for _ in range(10)]
    num_likes = [i for i in range(10)]
    parents = [1 for _ in range(10)]
    timestamps = ["2021-09-09 02:30:00" for _ in range(10)]
    bodies = [f"Answer #{num}" for num in range(10)]
    for user, tid, nlike, parent, time, bodi in zip(users, thread_ids, num_likes, parents, timestamps, bodies):
        try:
            db.session.add(Comment(user_id=user, thread_id=tid, likes=nlike, parent_id=parent, timestamp=time, body=bodi))
        except exc.IntegrityError:
            print("error")
            continue
    db.session.commit()
