from flask import current_app as app

from flask import request, jsonify
from flask_login import LoginManager, login_user, logout_user
import bcrypt
from flask_login.utils import login_required
from .models import Users
from .models import Thread

from .query import read_queries, write_queries

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    print("pass")
    return Users.query.get(int(user_id))

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
        passwordToByte = password.encode('utf8')

        encrypted_password = read_queries.get_encrypted_password(username)
        # print(encrypted_password)
        # print(type(encrypted_password))
        # print(type(bcrypt.hashpw(passwordToByte, bcrypt.gensalt(10))))

        if (encrypted_password != None):
            # only uncomment when testing (in case we manually add password without encrypt lol)
            # encrypted_password = bcrypt.hashpw(str.encode(encrypted_password), bcrypt.gensalt(10))
            if (bcrypt.checkpw(passwordToByte, encrypted_password.encode('utf8'))):
                current_user = Users.query.filter(Users.username == username).first()
                login_user(current_user, remember=True)
                return jsonify(username=username, status=True, message="Login successfully")
    return jsonify(username="", status=False, message="Can not login")

@app.route('/api/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    sky_user = request.form.get('sky_username')
    email = request.form.get('email')

    if (username != None and password != None and sky_user != None and email != None):
        write_queries.register_client(sky_user,username,password, email)
        return jsonify(username=username, status=True)
    return jsonify(username=username, status=False)
    

@app.route('/api/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify(status=True)

# Thread attempt begins here
@app.route('/threads/new_thread', methods=['POST'])
def create_thread():
    """ Route/function to create a new thread """

    # I assume we will be getting the thread information from the form they submit
    question_title = request.form.get('title')
    question_body = request.form.get('question-body')
    
    error_msg = 'OH NO HELP'
    user_id = request.args.get('user_id', error_msg) # Need to get userID somehow

    if (user_id == error_msg):
        return jsonify(status=False, message="request.args.get('user_id') couldn't get the user_id")

    # This can probably be handled in frontend but yah
    if (question_title == None):
        return jsonify(status=False, message="Thread title required.")
    
    # Perhaps not required
    if (question_body == ""):
        question_body = None
    
    write_queries.add_thread(question_title, user_id, question_body)
    return jsonify(status=True, message="Thread has been created.")

@app.route('/threads/<int:thread_id>/edit', methods=["POST"])
def edit_thread(thread_id):

    new_question_title = request.form.get('title')
    new_question_body = request.form.get('question-body')
    
    write_queries.edit_thread(thread_id, new_question_title, new_question_body)
    return jsonify(status=True, message="Updated thread successfully")

# @app.route('/api/test', methods=['GET'])
# def test():
    # return "Login as " + str(current_user)

