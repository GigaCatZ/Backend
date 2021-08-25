from flask import Flask, session, request, jsonify
from flask_login import LoginManager, login_user, logout_user, UserMixin
import bcrypt
from flask_login.utils import login_required
from .modules import *


class Flask_login_User(UserMixin):
    pass

users = []
users.append(User(username="admin", password=bcrypt.hashpw(b'12345', bcrypt.gensalt(10)), email="admin@muic.com"))


app = Flask(__name__)
app.secret_key = "muicpeeps12345"

# login_manager = LoginManager()
# login_manager.init_app(app)

# @login_manager.user_loader
# def user_loader(email):
    # if email not in users:
        # return
# 
    # user = User()
    # user.id = email
    # return user
# 
# 
# @login_manager.request_loader
# def request_loader(request):
    # email = request.form.get('email')
    # if email not in users:
        # return
# 
    # user = User()
    # user.id = email
    # return user

@app.route('/login', methods=['POST', 'GET'])
def login():
    def searchUser():
        # will change after we have database
        searchUser = [i for i in users if (i.username == username)]
        if (len(searchUser) == 0):
            return None
        return searchUser[0]
        
    if request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='username' id='username' placeholder='username'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit'/>
               </form>
               '''

    username = request.form.get('username')
    password = request.form.get('password')
    
    if (username != None and password != None):
        passwordToByte = str.encode(password)

        userFromDatabase = searchUser()

        if (userFromDatabase != None):
            if (bcrypt.checkpw(passwordToByte, userFromDatabase.password)):
                # change to Flask soon
                # current_user = Flask_login_User()
                # current_user.username = username
                # login_user(current_user)
                session['username'] = username
                return jsonify(username=username, status=True, message="Login successfully")
    return jsonify(username="", status=False, message="Can not login")


@app.route('/test')
def test():
    current_user = session.get('username')
    if (current_user == None):
        return "Not login yet"
    return "Login as " + str(session.get('username'))

@app.route('/logout', methods=['GET'])
def logout():
    session['username'] = None
    return "Logout"



@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

if __name__ == '__main__':
    app.run(debug=True)
