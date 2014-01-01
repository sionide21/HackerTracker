import os
from flask import Flask, request, abort, session
from hackertracker.database import Session, Model
from hackertracker.event import Event
from sqlalchemy import create_engine


app = Flask(__name__)
Session.configure(bind=create_engine(os.environ['DATABASE_URL']))


@app.route('/track/<thing>')
def track(thing):
    thing = thing.replace('_', ' ')
    event = Event.for_name(thing)
    event.track()
    return "You logged a '%s'" % event.name


@app.route('/')
def index():
    return "<br/>".join(e.name for e in Event.all())


@app.before_request
def setup_session():
    Session()


@app.teardown_request
def remove_session(exc):
    if exc:
        Session.rollback()
    else:
        Session.commit()
    Session.remove()


if __name__ == "__main__":
    app.run(debug=True)
