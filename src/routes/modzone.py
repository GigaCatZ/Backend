from flask import current_app as app
from flask import request, jsonify, redirect
from flask_login import current_user

from ..database.query import read_queries
from ..database.update_db import write_queries


@app.route("/api/modzone", methods=['GET'])
def get_info_for_mods():
    if not current_user.is_authenticated or not current_user.mod:
        return redirect("https://iccourses.cs.muzoo.io/modzone/access")
    threads, _, _ = read_queries.get_thread_by_order("SEARCH")
    users = read_queries.get_users()
    return jsonify(threads=threads, users=users)


@app.route("/api/modzone/set_moderator", methods=["POST"])
def set_moderator():
    if (current_user.is_authenticated and current_user.mod):
        candidate_username = request.form.get("candidate_username")
        if candidate_username == current_user.sky_username:
            return jsonify(status=False, message="You cannot remove yourself from moderator!!")
        candidate = read_queries.get_user_from_username(candidate_username)
        modval = request.form.get("modval")  # Intended to be bool
        if (modval.lower() == "false"):
            modval = False
        else:
            modval = True
        success = write_queries.change_user_modval(candidate_username, modval)

        if (success):
            return jsonify(status=True,
                           message="Successfully set moderator status of %s to %r" % (candidate_username, modval))
        else:
            return jsonify(status=False, message="Moderator status of %s is already %r" % (candidate_username, modval))

    return jsonify(status=False, message="Unable to access: current user is not moderator")


@app.route("/api/modzone/password_change", methods=["POST"])
def password_change():
    if (current_user.is_authenticated and current_user.mod):
        # Took 20 minutes to think of a name for this T_T
        requested_change_username = request.form.get("requested_change_username")
        new_password = request.form.get("new_password")
        write_queries.change_user_password(requested_change_username, new_password)
        return jsonify(status=True, message="Successfully changed password.")

    return jsonify(status=False, message="Unable to access: current user is not moderator")


@app.route("/api/modzone/add_tag", methods=['POST'])
def add_tag():
    if not current_user.is_authenticated or not current_user.mod:
        return jsonify(status=False, message="You are not a moderator. You cannot add custom tags.")

    course_id = request.form.get('course_id')
    course_name = request.form.get('course_name')
    if write_queries.add_tag(course_id, course_name):
        return jsonify(status=True, message="Successfully added the custom tag")
    return jsonify(status=False, message="This course ID already exists in our existing tags.")


@app.route("/api/modzone/merge_threads", methods=['POST'])
def merge_threads():
    if not current_user.is_authenticated or not current_user.mod:
        return jsonify(status=False, message="You are not a moderator. You cannot merge threads.")

    thread_a = request.form.get('thread_a')
    thread_b = request.form.get('thread_b')

    if thread_a == "" or thread_b == "":
        return jsonify(status=False, message="You need to select at least one thread")
    else:
        thread_a, thread_b = int(thread_a), int(thread_b)

    if thread_a == thread_b:  # just in case (who knows someone might accidentally merge the same thread with itself)
        return jsonify(status=False, message="Both IDs are the same! You can't merge a thread with itself!!! :(")

    if thread_b < thread_a: thread_a, thread_b = thread_b, thread_a

    if write_queries.merge_threads(thread_a, thread_b):
        return jsonify(status=True, message="Merge successful!")
    else:
        return jsonify(status=False, message="At least one thread does not exist!")
