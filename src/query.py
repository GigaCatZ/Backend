from .models import (Thread, db)
from .models import (Users, db)

class ReadOnly:
    def get_encrypted_password(self, username):
        user = Users.query.filter(Users.username == username)
        # print('\n\n\n========== AHHHH' + user)
        return user.first().encrypted_password if user is not None and user.first() is not None else None

read_queries = ReadOnly()
