from database import Model, Session
from datetime import datetime
from lib import returnit
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.sql.expression import func


class Event(Model):
    name = Column(String(100), index=True)
    created_at = Column(DateTime, default=func.now())
    _entries = relationship("Entry", order_by="-Entry.when", backref=backref("event"), lazy='dynamic')

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
    when = Column(DateTime)
    _attrs = relationship("Attribute", backref=backref("entry"), collection_class=attribute_mapped_collection("key"))
    attrs = association_proxy("_attrs", "value", creator=lambda k, v: Attribute(key=k, value=v))

    def __init__(self, when=None, attrs=None):
        self.when = when or datetime.now()
        self.attrs = attrs or {}


class Attribute(Model):
    entry_id = Column(Integer, ForeignKey('entry.id'))
    key = Column(String(100))
    value = Column(String(100))
