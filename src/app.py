import os
from flask import Flask, request, abort, session, render_template
from hackertracker.database import Session, Model
from hackertracker.event import Event
from sqlalchemy import create_engine


app = Flask(__name__)
Session.configure(bind=create_engine(os.environ['DATABASE_URL'], echo=True))


@app.route('/track/<thing>', methods=['GET', 'POST'])
def track(thing):
    event = Event.for_name(thing.replace('_', ' '))
    event.track(attrs=request.form)
    return ""


@app.route('/event/<thing>', methods=['GET', 'POST'])
def event(thing):
    event = Event.for_name(thing.replace('_', ' '))
    return render_template("event.html", event=event)


@app.route('/')
def index():
    return render_template("index.html", events=Event.all())


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
