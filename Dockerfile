FROM python:3.9-slim

WORKDIR /usr/src/app

RUN pip install --upgrade pip
RUN pip install pipenv

COPY ./Pipfile* /tmp/
RUN cd /tmp && pipenv lock --requirements > /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# Copy all our source files into the app folder
COPY . /usr/src/app/

# Tell Docker we're expected to expose port 5000
EXPOSE 5000

# Set the entry point
ENTRYPOINT ["gunicorn", "--bind", ":5000", "--workers", "4", "src.wsgi:app"]

