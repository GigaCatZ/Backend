PIPENV=pipenv
PYLIB=flask

all: build run

build:
	$(PIPENV) --python 3.9
	$(PIPENV) install $(PYLIB)

run:
	$(PIPENV) shell

