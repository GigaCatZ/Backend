from sqlalchemy import (event, exc)

from .models import *


@event.listens_for(Tag.__table__, 'after_create')
def create_tags(*args, **kwargs):
    # courses = ['MUIC', 'ICCS205', 'ICCS206', 'ICCS309', 'ICMA106', 'ICMA213', 'ICPY101', 'ICPY102', 'ICPY105', 'ICCS101', 'ICCS121', 'ICCS161', 'ICCS204', 'ICCS225', 'ICCS227', 'ICCS311', 'ICCS312', 'ICCS370', 'ICMA216', 'ICMA223', 'ICCS208']
    course_ids = ['ICCS205', 'ICCS206', 'ICCS121', 'ICCS101', 'ICCS204']
    course_names = ['Numerical Computations', 'Discrete Mathematics', 'System Skills and Low-level Programming',
                    'Introduction to Computer Programming', 'Data Structures and Object-Oriented Programming']
    for course_id, course_name in zip(course_ids, course_names):
        try:
            db.session.add(Tag(course_id=course_id, name=course_name, count=0))
        except exc.IntegrityError:
            continue
    db.session.commit()
