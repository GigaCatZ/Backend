from flask import current_app as app
from flask import redirect

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return redirect("https://iccourses.cs.muzoo.io/", code=404)