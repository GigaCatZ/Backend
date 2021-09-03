from flask import current_app as app
from flask import request, jsonify

from ..database.update_db import write_queries
from ..database.query import read_queries

@app.route("/api/modzone/add_mod")
def add_moderator():
    pass # imma add this so no errors, when merging just delete this line and put in Justin's code

@app.route("/api/modzone/add_tag", methods=['POST'])
def add_tag():
    if not read_queries.get_user_from_username(request.form.get('sky_username')).mod:
        return jsonify(status=False, message="You are not a moderator. You cannot add custom tags.")

    course_id = request.form.get('course_id')
    course_name = request.form.get('course_name')
    if write_queries.add_tag(course_id, course_name): 
        return jsonify(status=True, message="Successfully added the custom tag")
    return jsonify(status=False, message="This course ID already exists in our existing tags.")


@app.route("/api/modzone/merge_threads", methods=['POST'])
def merge_threads():
    if not read_queries.get_user_from_username(request.form.get('sky_username')).mod:
        return jsonify(status=False, message="You are not a moderator. You cannot merge threads.")
    
    thread_a = request.form.get('thread_a')
    thread_b = request.form.get('thread_b')

    if thread_a == thread_b: # just in case (who knows someone might accidentally merge the same thread with itself)
        return jsonify(status=False, message="Both IDs are the same! You can't merge a thread with itself!!! :(")

    if int(thread_b) < int(thread_a): thread_a, thread_b = thread_b, thread_a
    
    if write_queries.merge_threads(thread_a, thread_b):
        return jsonify(status=True, message="Merge successful!")
    else:
        return jsonify(status=False, message="At least one thread does not exist!") 
