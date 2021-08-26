from flask import current_app as app

from flask import request, jsonify
from flask_login import LoginManager, login_user, logout_user, current_user
import bcrypt
from sqlalchemy.exc import IntegrityError

from .query import read_queries, write_queries

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return read_queries.get_user_from_id(user_id)



@app.route('/api/whoami', methods=['GET'])
def authenticate():
    if (current_user.is_authenticated):
        return jsonify(is_logged_in=True, display_name=current_user.display_name, sky_username=current_user.sky_username)
    else:
        return jsonify(is_logged_in=False, display_name="", sky_username="")

@app.route('/api/login', methods=['POST'])
def login():
    username = request.form.get('sky_username')
    password = request.form.get('password')
    
    if (current_user.is_authenticated):
        return jsonify(username=current_user.sky_username, status=True, message="You already log in")

    if (username != None and password != None):
        passwordToByte = password.encode('utf8')

        encrypted_password = read_queries.get_encrypted_password(username)

        if (encrypted_password != None):
            if (bcrypt.checkpw(passwordToByte, encrypted_password.encode('utf8'))):
                cur_user = read_queries.get_user_from_username(username)
                login_user(cur_user, remember=True)
                return jsonify(username=username, status=True, message="Login successfully")
    return jsonify(username="", status=False, message="Can not login")

@app.route('/api/register', methods=['POST'])
def register():
    display_name = request.form.get('display_name')
    password = request.form.get('password')
    username = request.form.get('sky_username')

    if (username is not None and password is not None and display_name is not None):
        try:
            write_queries.register_client(username, display_name, password)
            return jsonify(username=username, status=True, message="Registered successfully!")
        except (IntegrityError):
            return jsonify(username=username, status=False, message="Username or Display Name has already been taken")
    return jsonify(username=username, status=False, message="Fields must not be empty")
    

@app.route('/api/logout', methods=['GET','POST'])
def logout():
    if(current_user.is_authenticated):
        user = current_user.sky_username
        logout_user()
        return jsonify(status=True, username=user, message="Logout successfully")
    else:
        return jsonify(status=False, username="", message="User hasnt logged in yet")

@app.route('/api/test', methods=['GET'])
def test():
    try:
        return "Login as " + str(current_user.username)
    except (AttributeError):
        return "Not login yet"
    return jsonify(status=True)

# Thread attempt begins here
@app.route('/api/new_thread', methods=['POST'])
def create_thread():
    """ Route/function to create a new thread """

    # I assume we will be getting the thread information from the form they submit
    question_title = request.form.get('title')
    question_body = request.form.get('question-body')
    
    error_msg = 'OH NO HELP'
    # will change back to args, depending on how frontend chooses to send the username to us
    username = request.form.get('sky_username', error_msg) # Need to get userID somehow

    if (username == error_msg):
        return jsonify(status=False, message="request.args.get('username') couldn't get the user_id")

    # This can probably be handled in frontend but yah
    if (question_title == None):
        return jsonify(status=False, message="Thread title required.")
    
    # Perhaps not required
    if (question_body == ""):
        question_body = None
    
    write_queries.add_thread(question_title, username, question_body, request.form.get('tags'))
    return jsonify(status=True, message="Thread has been created.")


# will test this later once we confirm how frontend gonna do this
@app.route('/threads/<int:thread_id>/edit', methods=['POST'])
def edit_thread(thread_id):

    new_question_title = request.form.get('title')
    new_question_body = request.form.get('question-body')
    
    write_queries.edit_thread(thread_id, new_question_title, new_question_body)
    return jsonify(status=True, message="Updated thread successfully")

# Potential way to display an individual thread
@app.route('/threads/<int:thread_id>')
def display_thread(thread_id: int):
    thread = Thread.query.filter(Thread.id == thread_id)
    return jsonify(title=thread.question, body=thread.body, user=thread.user_id, date_asked=thread.timestamp)


