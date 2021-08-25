PIPENV=pipenv
PYLIB=flask PyMySQL flask_sqlalchemy flask-login bcrypt

all: clean install run_env

install:
	$(PIPENV) --python 3.9
	$(PIPENV) install $(PYLIB)

run_env:
	$(PIPENV) shell

run:
	FLASK_APP=src/app flask run

clean:
	rm -rf Pipfile Pipfile.lock

