from database import Model, Session
from datetime import datetime
from lib import returnit
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.exc import NoResultFound


class Event(Model):
    name = Column(String(100), index=True)
    _entries = relationship("Entry", order_by="-Entry.created_at", backref=backref("event"))

    def __init__(self, name):
        self.name = name

    def track(self, *args, **kwargs):
        return returnit(self._entries.append, Entry(*args, **kwargs))

    def entries(self):
        return self._entries

    @classmethod
    def all(cls):
        return Session.query(cls).order_by('name').all()

    @classmethod
    def for_name(cls, name):
        try:
            return Session.query(cls).filter_by(name=name).one()
        except NoResultFound:
            return returnit(Session.add, cls(name))


class Entry(Model):
    event_id = Column(Integer, ForeignKey('event.id'))

    def __init__(self, when=None, attrs=None):
        self.when = when or datetime.now()
        self.attrs = attrs or {}
