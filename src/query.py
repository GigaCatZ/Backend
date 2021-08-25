from .models import (Thread, db)
from .models import (Users, db)

class ReadOnly:
    def get_encrypted_password(self, username):
        user = Users.query.filter(Users.username == username).first()
        return user.encrypted_password if user is not None else None

read_queries = ReadOnly()
