from flask import current_app as app

from flask import request, jsonify
from flask_login import LoginManager, login_user, logout_user
import bcrypt
from flask_login.utils import login_required
from .models import Users


from .query import read_queries

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(username):
    print("pass")
    return Users.query.get(username)

# THIS IS A DUMMY THING COPIED FROM AJ KANAT


@app.route('/login', methods=['GET'])
def get_login():
    return '''
               <form action='api/login' method='POST'>
                <input type='text' name='username' id='username' placeholder='username'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit'/>
               </form>
            '''

@app.route('/api/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if (username != None and password != None):
        passwordToByte = str.encode(password)

        encrypted_password = read_queries.get_encrypted_password(username)

        if (encrypted_password != None):
            # only uncomment when testing (in case we manually add password without encrypt lol)
            # encrypted_password = bcrypt.hashpw(str.encode(encrypted_password), bcrypt.gensalt(10))
            if (bcrypt.checkpw(passwordToByte, encrypted_password)):
                current_user = Users.query.filter(Users.username == username).first()
                login_user(current_user, remember=True)
                return jsonify(username=username, status=True, message="Login successfully")
    return jsonify(username="", status=False, message="Can not login")

@app.route('/api/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify(status=True)

# @app.route('/api/test', methods=['GET'])
# def test():
    # return "Login as " + str(current_user.id)

