from flask_login import UserMixin

class User:
    def __init__(self, username, password,email) -> None:
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return f'<User: {self.username}>'


class Flask_login_User(UserMixin):
    pass
