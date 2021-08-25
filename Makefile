PIPENV=pipenv
PYLIB=flask PyMySQL flask_sqlalchemy

all: install run_env

install:
	$(PIPENV) --python 3.9
	$(PIPENV) install $(PYLIB)

run_env:
	$(PIPENV) shell

run:
	FLASK_APP=app flask run

