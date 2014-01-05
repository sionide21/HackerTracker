import bmemcached
import logging
import os
from flask import Flask, request, abort, session, redirect, render_template, make_response, url_for
from flask.ext import memcache_session
from functools import wraps
from hackertracker.database import Session, is_database_bound
from hackertracker.event import Event, EventNotFound
from openid.consumer.consumer import Consumer
from openid.store.memstore import MemoryStore
from sqlalchemy import create_engine
from werkzeug.contrib.fixers import ProxyFix


logging.basicConfig(level=logging.INFO)


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
use_openid = False
if 'MEMCACHEDCLOUD_SERVERS' in os.environ and 'OPENID_AUTH_IDENTITY' in os.environ:
    use_openid = True
    app.cache = bmemcached.Client(
        os.environ['MEMCACHEDCLOUD_SERVERS'].split(','),
        os.environ.get('MEMCACHEDCLOUD_USERNAME'),
        os.environ.get('MEMCACHEDCLOUD_PASSWORD')
    )
    app.session_interface = memcache_session.Session()
    openid_store = MemoryStore()
    openid_identity = os.environ["OPENID_AUTH_IDENTITY"]


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


def check_openid_credentials(fn):
    if not use_openid:
        return fn

    @wraps(fn)
    def _fn(*args, **kwargs):
        if not session.get('logged_in', False):
            c = Consumer(session, openid_store)
            url = c.begin(openid_identity).redirectURL(url_for('index', _external=True), url_for('verify_identity', _external=True))
            return redirect(url)
        else:
            return fn(*args, **kwargs)
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
        for f in kwargs.pop('before', [check_openid_credentials]):
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
@check_openid_credentials
def index():
    return render_template("index.html", events=Event.all())


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return render_template("logout.html")


@app.route('/verify_identity')
def verify_identity():
    if not use_openid:
        abort(404)
    c = Consumer(session, openid_store)
    r = c.complete(request.args, request.base_url)
    if r.status == "success" and r.identity_url == openid_identity:
        session['logged_in'] = True
        return redirect('/')
    else:
        abort(403)


@app.before_request
def setup_session():
    Session()


@app.teardown_request
def remove_session(exc):
    if exc:
        logging.getLogger(__name__).error("Rolling back database: %s", exc)
        Session.rollback()
    else:
        Session.commit()
    Session.remove()


if __name__ == "__main__":
    app.run(debug=True)
