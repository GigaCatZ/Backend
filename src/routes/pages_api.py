
from flask import current_app as app

from flask import request, jsonify
from sqlalchemy.exc import IntegrityError

from ..database.query import read_queries
from ..database.update_db import write_queries
from ..database.models import Thread, Comment

@app.route('/api/search', methods=['POST'])
def search():
    def filter_by_tags(thread, search_tags):
        return len([tag for tag in thread['tags'] if (tag.lower() == search_tags)]) != 0

    def filter_by_title(thread, search_title):
        return set(search_input.split()) - set(thread['title'].split()) == set() or \
            search_title in thread['title'].lower()

    def filter_by_display_name(thread, search_display_name):
        return thread['display_name'].lower() == search_display_name

    search_input = request.form.get('search_input')
    type_search = request.form.get('type_search')
    filter_function = filter_by_title

    all_types = {'tag': filter_by_tags, 'title': filter_by_title, 'author': filter_by_display_name}
    if (type_search != None):
        type_search_lower_case = type_search.lower()
        for each_type in all_types:
            if (type_search_lower_case == each_type):
                filter_function = all_types[each_type]
                if (each_type == 'tag'):
                    search_input = search_input.split('|')[0].strip()
                break
        del type_search_lower_case

    thread_search = read_queries.get_thread_by_order('SEARCH')
    search_input_lower_case = search_input.lower()
    result = [thread for thread in thread_search[0] if (filter_function(thread, search_input_lower_case))]
    #   delete all objects before return
    del search_input_lower_case
    del search_input
    del type_search
    del all_types
    del thread_search
    del filter_function
    return jsonify(search_result=result)


@app.route('/api/home', methods=['POST'])
def homepage():
    order = request.form.get('order')
    threads, status, message = read_queries.get_thread_by_order(order)
    return jsonify(tags=read_queries.display_top_tags(), order=order, threads=threads, message=message, status=status)


# gets top 5 threads by dupes for FAQ page
@app.route("/api/faq", methods=["GET"])
def get_top_threads():
    topFive = []
    queried = read_queries.get_thread_by_dupe()
    comments = [read_queries.get_top_comment(thread.id) for thread in queried if thread != None]

    for thread, comment in zip(queried, comments):
        if comment == None:
            continue
        tmp = {
            "title": thread.question,
            "body": thread.body,
            "answer": comment.comment_body
        }
        topFive.append(tmp)

    res = {"response": topFive}
    return jsonify(res)

# gets all of the available tags
@app.route("/api/get_tags", methods=["GET"])
def send_all_tags():
    queried = read_queries.get_all_tags()
    return jsonify(tags=[{"id": tag.id, "course_id": tag.course_id, "name": tag.name, "count": tag.count} for tag in queried if tag != None])
