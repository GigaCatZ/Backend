from flask import current_app as app

from flask import request, jsonify
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from ..database.query import read_queries
from ..database.update_db import write_queries

# COMMENT ATTEMPT BEGINS HERE (I'm just sticking with the format I used earlier, can change if frontend doesn't like it)
@app.route('/api/new_comment', methods=['POST'])
def new_comment():
    if not current_user.is_authenticated:
        return jsonify(status=False, message="User is not logged in", thread_id=None, parent_id=None, comment_id=None, username=None) 

    comment_body = request.form.get("comment_body")

    if (comment_body is None or len(comment_body.strip()) == 0):
        return jsonify(status=False, message="Empty comment body", thread_id=None, parent_id=None, comment_id=None, username=None)
    thread_id = request.form.get('thread_id')

    parent_id = request.form.get('parent_id')

    try:
        comment_id = write_queries.add_comment(thread_id, comment_body, parent_id)
        return jsonify(comment_id=comment_id, username=current_user.sky_username, thread_id=thread_id, parent_id=parent_id, status=True, message="Comment created successfully")
    except(IntegrityError):
        return jsonify(status=False, message="Parent comment does not exist", thread_id=None, parent_id=None, comment_id=None, username=None)


@app.route('/api/edit_comment', methods=["POST"])
def edit_comment():
    if not current_user.is_authenticated:
        return jsonify(status=False, message="User is not logged in", thread_id=None, parent_id=None, comment_id=None, username=None) 

    comment_id = request.form.get("comment_id")
    user_id = current_user.id
    comment = read_queries.get_comment_by_id(comment_id)
    new_comment_body = request.form.get("comment_body")
    
    if (user_id == comment.user_id):
        if (len(new_comment_body.strip()) == 0):
            return jsonify(status=False, message="Empty comment body")

        write_queries.edit_comment(comment_id, new_comment_body)
        return jsonify(status=True, message="Comment edited successfully")
    
    return jsonify(status=False, message="Unable to edit: user is not the owner of the comment")

@app.route("/api/delete_comment", methods=["POST"])
def delete_comment():
    if not current_user.is_authenticated:
        return jsonify(status=False, message="User is not logged in", thread_id=None, parent_id=None, comment_id=None, username=None) 

    # Again, defaulting to request.form.get until we have a way to request
    comment_id = request.form.get("comment_id")
    user_id = current_user.id
    comment = read_queries.get_comment_by_id(comment_id)

    if (user_id == comment.user_id):
        write_queries.delete_comment(comment_id)
        return jsonify(status=True, message="Comment deleted successfully")
    
    return jsonify(status=False, message="Unable to delete: user is not the owner of the comment")

@app.route("/api/like_comment", methods=["POST"])
def like_comment():
    comment_id = request.form.get('comment_id')
    
    try:
        if not current_user.is_authenticated: return jsonify(status=False, liked_comment=False, message="User is not logged in!", comment_id=comment_id, new_likes=read_queries.get_comment_like_count(comment_id), username=None)
        comment, liked, message = write_queries.upvote_comment(comment_id)
        return jsonify(status=True, liked_comment=liked, message=message, comment_id=comment.id, new_likes=comment.likes, username=current_user.sky_username)
    except(AttributeError):
        jsonify(status=False, liked_comment=None, message="Comment does not exist", comment_id=None, new_likes=None, username=None)

    return jsonify(status=False, liked_comment=None, message="There's an error", comment_id=None, new_likes=None, username=None)
    
