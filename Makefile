PIPENV=pipenv
PYLIB=flask flask-login bcrypt

all: install run_env

install:
	$(PIPENV) --python 3.9
	$(PIPENV) install $(PYLIB)

run_env:
	$(PIPENV) shell

run:
	FLASK_APP=src/app flask run

