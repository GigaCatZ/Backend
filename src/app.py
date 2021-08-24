from flask import Flask, session, request
# from flask_login import LoginManager
import bcrypt


class User:
    def __init__(self, username, password,email) -> None:
        self.username = username
        self.password = password
        self.email = email

    def __repr__(self):
        return f'<User: {self.username}>'

users = []
users.append(User(username="admin", password=bcrypt.hashpw(b'12345', bcrypt.gensalt(10)), email="admin@muic.com"))


app = Flask(__name__)
app.secret_key = "muicpeeps12345"

# login_manager = LoginManager()
# login_manager.init_app(app)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if (username != None and password != None):
        passwordToByte = str.encode(password)

        searchUser = [i for i in users if (i.username == username)]
        if (len(searchUser) != 0):
            if (bcrypt.checkpw(passwordToByte, searchUser[0].password)):
                session['username'] = username
                return True
            else:
                return False
    return False



@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True)
