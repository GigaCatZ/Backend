from flask import current_app as app

from flask import request, jsonify
from sqlalchemy.exc import IntegrityError

from ..database.query import read_queries
from ..database.update_db import write_queries
from ..database.models import Thread, Comment

@app.route('/api/getthread', methods=['POST'])
def get_thread_info():
    thread = read_queries.get_thread_by_id(request.form.get('thread_id'))
    username = request.form.get('sky_username')
    try:
        return jsonify(status=True, thread_id=thread.id, author=read_queries.get_user_from_id(thread.user_id).display_name, title=thread.question, is_liked=(read_queries.check_thread_like(thread.id, username) is not None),\
            body=thread.body, timestamp=thread.timestamp, likes=thread.likes, comments=read_queries.get_comments_of_thread(thread.id, username), tags=read_queries.get_tags_from_thread(thread.id))
    except(AttributeError):
        return jsonify(status=False, thread_id=None, author=None, title=None, body=None, timestamp=None, likes=None, comments=None, tags=None, is_liked=False)


@app.route("/api/like_thread", methods=["POST"])
def like_thread():
    username = request.form.get('username')
    thread_id = request.form.get('thread_id')
    try:
        if username == "": return jsonify(status=False, liked_thread=False, message="User is not logged in!", thread_id=thread_id, new_likes=read_queries.get_thread_like_count(thread_id), username=username)
        thread, liked, message = write_queries.upvote_thread(thread_id, username)
        return jsonify(status=True, liked_thread=liked, message=message, thread_id=thread.id, new_likes=thread.likes, username=username)
    except(AttributeError):
        jsonify(status=False, liked_thread=None, message="Thread does not exist", thread_id=None, new_likes=None, username=None)

@app.route('/api/deletethread', methods=['POST'])
def delete_thread():
    """ Route/function to delete a thread """ 

    thread_id = request.form.get('thread_id')
    username = request.form.get('sky_username')
    user_id = read_queries.get_id_from_username(username)
    thread = read_queries.get_thread_by_id(thread_id) 
    
    if (user_id == thread.user_id):
        write_queries.delete_thread(thread_id)
        return jsonify(status=True, message="Successfully deleted thread")

    return jsonify(status=False, message="Unable to delete: user does not own the thread.")


# will test this later once we confirm how frontend gonna do this
@app.route('/api/edit_thread', methods=['POST'])
def edit_thread():
    """ Route/function to edit a thread """

    thread_id = request.form.get("thread_id")
    username = request.form.get("sky_username")
    user_id = read_queries.get_id_from_username(username)
    thread = read_queries.get_thread_by_id(thread_id)

    if (user_id == thread.user_id):
        new_question_tags = request.form.get('tags')
        new_question_body = request.form.get('text')

        if new_question_tags == "": new_question_tags = set()
        else: new_question_tags = set(new_question_tags.split(','))
        
        write_queries.edit_thread(thread_id, new_question_tags, new_question_body)
        return jsonify(status=True, message="Updated thread successfully")
    
    return jsonify(status=False, message="Unable to edit: user does not own the thread")

# will test this later once we confirm how frontend gonna do this
@app.route('/api/edit_thread', methods=['GET'])
def info_for_edit_thread():
    """ What frontenders need to edit thread """

    thread_id = request.args.get("thread_id")
    thread = read_queries.get_thread_by_id(thread_id)
    
    return jsonify(courses=read_queries.display_all_tags(), selected_tags=read_queries.get_tags_from_thread(thread_id), title=thread.question, body=thread.body)

@app.route('/api/create_thread', methods=['GET'])
def get_all_tags():
    return jsonify(courses=read_queries.display_all_tags())

# Thread attempt begins here
@app.route('/api/create_thread', methods=['POST'])
def create_thread():
    """ Route/function to create a new thread """

    # I assume we will be getting the thread information from the form they submit
    question_title = request.form.get('title')
    question_body = request.form.get('text')

    # will change back to args, depending on how frontend chooses to send the username to us
    username = request.form.get('username') # Need to get userID somehow
    tags = request.form.get('tags')

    if (username == None):
        return jsonify(status=False, username=None, thread_id=None, title=None, tags=None, message="Couldn't get the username")

    # This can probably be handled in frontend but yah
    if (question_title == None):
        return jsonify(status=False, username=None, thread_id=None, title=None, tags=None,  message="Thread title required.")

    # Perhaps not requiredt
    if (question_body == ""):
        question_body = None

    if tags == "": tags = []
    else: tags = tags.split(',')

    thread = write_queries.add_thread(question_title, username, question_body, tags)
    return jsonify(status=True, username=username, thread_id=thread.id, thread_title=thread.question, tags=tags,  message="Thread has been created.")
