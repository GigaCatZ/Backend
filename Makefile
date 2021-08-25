PIPENV=pipenv
PYLIB=flask flask-login bcrypt PyMySQL flask-sqlalchemy python-dotenv

init:
	$(PIPENV) --python 3.9
	$(PIPENV) install $(PYLIB)

run:
	FLASK_APP=src/app flask run
