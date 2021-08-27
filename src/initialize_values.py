from .models import (Tag, db)
from sqlalchemy import event, exc

@event.listens_for(Tag.__table__, 'after_create')
def create_tags(*args, **kwargs):
    print('triggered')
    courses = ['MUIC', 'ICCS205', 'ICCS206', 'ICCS309', 'ICMA106', 'ICMA213', 'ICPY101', 'ICPY102', 'ICPY105', 'ICCS101', 'ICCS121', 'ICCS161', 'ICCS204', 'ICCS225', 'ICCS227', 'ICCS311', 'ICCS312', 'ICCS370', 'ICMA216', 'ICMA223', 'ICCS208']
    for course in courses:
        try:
            db.session.add(Tag(id=course, count=0))
        except (exc.IntegrityError):
            continue
    db.session.commit()