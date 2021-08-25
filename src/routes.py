from flask import current_app as app

from flask import Flask, session, request, jsonify
from flask_login import LoginManager, login_user, logout_user, UserMixin
import bcrypt
from flask_login.utils import login_required

import os

from .query import read_queries


# THIS IS A DUMMY THING COPIED FROM AJ KANAT


@app.route('/login', methods=['GET'])
def get_login():
    return '''
               <form action='login' method='POST'>
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
                # change to Flask soon
                # current_user = Flask_login_User()
                # current_user.username = username
                # login_user(current_user)
                session['username'] = username
                return jsonify(username=username, status=True, message="Login successfully")
    return jsonify(username="", status=False, message="Can not login")

