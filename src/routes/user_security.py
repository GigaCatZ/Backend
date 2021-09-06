from flask import current_app as app

from flask import request, jsonify
from flask_login import LoginManager, login_user, logout_user, current_user
from sqlalchemy.exc import IntegrityError
import bcrypt

from ..database.query import read_queries
from ..database.update_db import write_queries
from ..database.models import Thread, Comment

from ..features.email import emailer

from random import choice
from string import ascii_letters, digits

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return read_queries.get_user_from_id(user_id)

@app.route('/api/checkuser', methods=['POST'])
def createuser():
    display_name = request.form.get('display_name')

    if (display_name != None):
        count = read_queries.get_user_from_display_name(display_name).count()
        if (count == 0):
            return jsonify(status=True, message="Display name is not taken yet")
        else:
            return jsonify(status=False, message="Display name already taken")
    return jsonify(status=False, message="Api does not get data")

@app.route('/api/whoami', methods=['GET'])
def authenticate():
    if (current_user.is_authenticated):
        return jsonify(is_logged_in=True, display_name=current_user.display_name, sky_username=current_user.sky_username, mod=current_user.mod)
    else:
        return jsonify(is_logged_in=False, display_name="", sky_username="", mod=False)

@app.route('/api/login', methods=['POST'])
def login():
    username = request.form.get('sky_username')
    password = request.form.get('password')
    remember = (request.form.get('remember')[0] == "t")

    if (current_user.is_authenticated):
        return jsonify(username=current_user.sky_username, status=True, message="You already log in")

    if (username != None and password != None):
        passwordToByte = password.encode('utf8')

        encrypted_password = read_queries.get_encrypted_password(username)

        if (encrypted_password != None):
            if (bcrypt.checkpw(passwordToByte, encrypted_password.encode('utf8'))):
                cur_user = read_queries.get_user_from_username(username)
                login_user(cur_user, remember = remember)
                return jsonify(username=username, status=True, message="Login successfully")
    return jsonify(username="", status=False, message="Incorrect Username or Password")

@app.route('/api/register', methods=['POST'])
def register():
    display_name = request.form.get('display_name')
    password = request.form.get('password')
    username = request.form.get('sky_username')
    email = request.form.get('email')

    if (username is not None and password is not None and display_name is not None):
        try:
            write_queries.register_client(username, display_name, password, email)
            emailer.registration_success_email(email, username, display_name)
            return jsonify(username=username, status=True, message="Registered successfully!")
        except (IntegrityError):
            return jsonify(username=username, status=False, message="Username, Display Name, or Email has already been taken")
    return jsonify(username=username, status=False, message="Fields must not be empty")

@app.route('/api/logout', methods=['GET','POST'])
def logout():
    if(current_user.is_authenticated):
        user = current_user.sky_username
        logout_user()
        return jsonify(status=True, username=user, message="Logout successfully")
    else:
        return jsonify(status=False, username="", message="User hasnt logged in yet")


@app.route("/api/change_info", methods=["POST"])
def update_info():
    username = current_user.sky_username
    password = request.form.get('current_password')

    display_name = request.form.get('display_name')
    new_password = request.form.get('new_password')

    if password is None or not bcrypt.checkpw(password.encode('utf8'), read_queries.get_encrypted_password(username).encode('utf8')):
        return jsonify(status=False, message="Incorrect password")
    
    # added the or clause so can personalize sending emails ONLY when changes is made
    if new_password is None or new_password==password: new_password = ""
    # if read_queries.get_user_from_display_name(display_name).first() is not None:
    #     return jsonify(status=False, message="This display name has already been taken")
    try:
        write_queries.update_user(display_name, new_password)
        return jsonify(status=True, message="Successfully updated user information!")
    except(IntegrityError):
        return jsonify(status=False, message="Display Name has already been taken")


@app.route('/api/new_password', methods=['POST'])
def forgot_password():
    def password_generator(size=15, chars=ascii_letters + digits):
        return ''.join(choice(chars) for _ in range(size))
    
    username = request.form.get('sky_username')
    email = request.form.get('email')

    if username is None or username=="":
        return jsonify(status=False, message="You need to specify your username!")
    user = read_queries.get_user_from_username(username)
    if user is None: return jsonify(status=False, message="There is no account registered with this username")
    actual_email = user.email
    if email is None or email=="" or email != actual_email:
        return jsonify(status=False, message='This is not the email you have registered with for this account!')
    
    write_queries.change_user_password(username, password_generator())
    return jsonify(status=True, message='The request has been sent. Your new password has been sent to you via Email! If you don\'t see any email, please check your spam folder.')
