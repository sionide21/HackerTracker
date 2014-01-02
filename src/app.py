import os
import logging
from flask import Flask, request, abort, session, render_template, make_response
from functools import wraps
from hackertracker.database import Session, Model, is_database_bound
from hackertracker.event import Event, EventNotFound
from sqlalchemy import create_engine


logging.basicConfig(level=logging.INFO)


app = Flask(__name__)
TOKEN = os.environ.get('AUTH_TOKEN')
if not is_database_bound():
    # Don't mess with the database connection if someone else set it up already
    Session.configure(bind=create_engine(os.environ['DATABASE_URL']))


def check_auth_token(fn):
    @wraps(fn)
    def _fn(*args, **kwargs):
        token = request.headers.get('X-Auth-Token', request.args.get('auth'))
        if TOKEN == token:
            return fn(*args, **kwargs)
        else:
            abort(403)
    return _fn


def event_controller(url=None, create=False, **kwargs):
    def _decorator(fn):
        @wraps(fn)
        def _controller(thing):
            try:
                event = Event.for_name(thing.replace('_', ' '), create=create)
            except EventNotFound:
                abort(404)
            return fn(event)
        for f in kwargs.pop('before', []):
            _controller = f(_controller)
        return app.route(url or '/%s/<thing>' % fn.__name__, **kwargs)(_controller)
    return _decorator


@event_controller(methods=['GET', 'POST'], create=True, before=[check_auth_token])
def track(event):
    event.track(attrs=request.form)
    return ""


@event_controller()
def event(event):
    return render_template("event.html", event=event)


@event_controller("/export/<thing>.csv")
def export_csv(event):
    resp = make_response(event.export_csv())
    resp.headers["Content-Type"] = "text/csv"
    resp.headers["Content-Disposition"] = "attachment;filename=%s.csv" % event.slug
    return resp


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
