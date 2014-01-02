from csv import writer as csv_writer
from database import Model, Session
from datetime import datetime
from lib import returnit
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import backref, relationship, subqueryload
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.sql.expression import func
from StringIO import StringIO


class Attribute(Model):
    entry_id = Column(Integer, ForeignKey('entry.id'))
    key = Column(String(100))
    value = Column(String(100))


class Entry(Model):
    event_id = Column(Integer, ForeignKey('event.id'))
    when = Column(DateTime)
    _attrs = relationship("Attribute", backref=backref("entry"), collection_class=attribute_mapped_collection("key"))
    attrs = association_proxy("_attrs", "value", creator=lambda k, v: Attribute(key=k, value=v))

    def __init__(self, when=None, attrs=None):
        self.when = when or datetime.now()
        self.attrs = attrs or {}

    def __str__(self):
        return self.when.strftime("%b %d, %Y %I:%M%p")


class Event(Model):
    name = Column(String(100), index=True)
    created_at = Column(DateTime, default=func.now())
    _entries = relationship("Entry", order_by=Entry.when.desc(), backref=backref("event"), lazy='dynamic')

    def __init__(self, name):
        self.name = name

    @property
    def slug(self):
        return self.name.replace(" ", "_")

    def track(self, *args, **kwargs):
        return returnit(self._entries.append, Entry(*args, **kwargs))

    def entries(self):
        return self._entries.options(subqueryload(Entry._attrs))

    def entry_count(self):
        return self._entries.count()

    def latest_entry(self):
        return self._entries.first()

    def attributes(self):
        return [x for x, in Session.query(Attribute.key)
                .join(Attribute.entry)
                .filter_by(event_id=self.id)
                .order_by("key").distinct()]

    def export_csv(self):
        out = StringIO()
        csv = csv_writer(out)
        attributes = self.attributes()
        headers = ["When"] + attributes
        csv.writerow(headers)
        for entry in self.entries():
            csv.writerow([entry.when] + [entry.attrs.get(x, "") for x in attributes])
        return out.getvalue()

    @classmethod
    def all(cls):
        return Session.query(cls).order_by('name').all()

    @classmethod
    def for_name(cls, name):
        try:
            return Session.query(cls).filter_by(name=name).one()
        except NoResultFound:
            return returnit(Session.add, cls(name))
