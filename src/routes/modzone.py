from flask import current_app as app
from flask import request, jsonify
from ..database.query import read_queries
from ..database.update_db import write_queries
from ..database.models import Thread, Comment, Users

@app.route("/api/modzone/set_moderator", methods=["POST"])
def set_moderator():

    username = request.form.get("sky_username")
    user = read_queries.get_user_from_username(username)
 
    if (user.mod):
        candidate_username = request.form.get("candidate_username")
        candidate = read_queries.get_user_from_username(candidate_username)
        modval = request.form.get("modval") # Intended to be bool
        if (modval.lower() == "false"):
            modval = False
        else:
            modval = True
        success = write_queries.change_user_modval(candidate_username, modval)
        
        if (success):
            return jsonify(status=True, message="Successfully set moderator status of %s to %r" % (candidate_username, modval))
        else:
            return jsonify(status=False, message="Moderator status of %s is already %r" % (candidate_username, modval))

    return jsonify(status=False, message="Unable to access: current user is not moderator")

@app.route("/api/modzone/password_change", methods=["POST"])
def password_change():

    username = request.form.get("sky_username")
    user = read_queries.get_user_from_username(username)

    if (user.mod):

        # Took 20 minutes to think of a name for this T_T
        requested_change_username = request.form.get("requested_change_username")
        new_password = request.form.get("new_password")
        write_queries.change_user_password(requested_change_username, new_password)
        return jsonify(status=True, message="Successfully changed password.") 

    return jsonify(status=False, message="Unable to access: current user is not moderator")
