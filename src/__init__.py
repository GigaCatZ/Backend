from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def create_app(test_config):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config.Config")

    db.init_app(app)

    with app.app_context():
        from .database import initialize_values
        from .routes import comments_api, threads_api, pages_api, user_security, modzone

        db.create_all() # Create database tables if not already there!

        return app

if __name__ == '__main__':
	app = create_app(None)
	app.run(host='0.0.0.0')
