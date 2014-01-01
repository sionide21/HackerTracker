import unittest
from datetime import datetime, timedelta
from hackertracker import event
from hackertracker.database import Model, Session
from sqlalchemy import create_engine


class TestEvents(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite:///:memory:', echo=True)
        Model.metadata.create_all(engine)
        Session.configure(bind=engine)

    def tearDown(self):
        Session.remove()

    def assertDatetimesEqual(self, w1, w2):
        "Assert datetimes are equal to the second"
        self.assertEqual(w1.replace(microsecond=0), w2.replace(microsecond=0))

    def test_get_event(self):
        e = event.Event.for_name("Drink glass of water")
        self.assertEqual(e.name, "Drink glass of water")

    def test_basic_track(self):
        e = event.Event.for_name("Drink glass of water")
        o = e.track()
        self.assertEqual(list(e.entries()), [o])

    def test_events_persist(self):
        e = event.Event.for_name("Drink glass of water")
        o = e.track(attrs=dict(size="16", location="office"))
        when = o.when
        attrs = dict(o.attrs)
        print attrs

        # Reload from db
        Session.commit()
        Session.remove()

        e = event.Event.for_name("Drink glass of water")
        o1 = e.entries()[0]
        self.assertDatetimesEqual(when, o1.when)
        self.assertEqual(attrs, o1.attrs)

    def test_entry_count(self):
        e = event.Event.for_name("Drink glass of water")
        e.track()
        e.track()
        e.track()
        Session.commit()
        self.assertEqual(e.entry_count(), 3)

    def test_list_events(self):
        e1 = event.Event.for_name("Drink glass of water")
        e2 = event.Event.for_name("Clean litter box")

        self.assertEqual(event.Event.all(), [e2, e1])

    def test_alternate_time(self):
        e = event.Event.for_name("Drink glass of water")
        o = e.track()
        self.assertDatetimesEqual(o.when, datetime.now())

        when = datetime.now() - timedelta(hours=10)
        o = e.track(when)
        self.assertDatetimesEqual(o.when, when)

    def test_attributes(self):
        e = event.Event.for_name("Drink glass of water")
        o = e.track(attrs=dict(size="16", location="office"))
        self.assertEqual(o.attrs, {
            "size": "16",
            "location": "office"
        })

    def test_list_attributes(self):
        e = event.Event.for_name("Drink glass of water")
        e.track(attrs=dict(size="16", location="office"))
        e.track(attrs=dict(hello="world"))
        e.track(attrs=dict(hello="goodbye", location="office"))
        event.Event.for_name("Fire ze missile").track(attrs=dict(le_tired="true"))
        Session.commit()
        self.assertEqual(e.attributes(), ["hello", "location", "size"])
