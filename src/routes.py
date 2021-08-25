from flask import current_app as app
from flask import (render_template, request, jsonify)
from flask.helpers import make_response
from .models import (Thread, db)
from .models import (Users, db)
from datetime import datetime as dt


# THIS IS A DUMMY THING COPIED FROM AJ KANAT

@app.route('/threads', methods=['POST'])
def create_message():
    required_fields = set(['author', 'message'])
    data = request.get_json()
    if not data or not (required_fields <= data.keys()):
        print(data, required_fields)
        return make_response(jsonify({'status': 'Bad Request'}), 400)
    author, message = data.get('author'), data.get('message')
    new_post = Thread(question=message, timestamp=dt.now(), dupes=1)
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"status": "OK"})

@app.route('/threads')
def list_messages():
    results = Thread.query.all()  # user .filter to scope it down (like a WHERE clause)
    # .all() everything matching this ..vs .first() only the first entry

    if request.args.get('pretty') == 'true':
        return render_template('display.html', messages=results)

    messages = "<br />".join(
        repr((m.id, m.user_id, m.question, m.timestamp, m.dupes)) for m in results
    )
    return messages
