import csv
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

    def test_latest_entry(self):
        e = event.Event.for_name("Drink glass of water")
        e.track(when=earlier(seconds=3))
        e.track(when=earlier(seconds=2))
        f = e.track(when=earlier(seconds=1))
        Session.commit()

        self.assertEqual(e.latest_entry().id, f.id)

    def test_display_entry(self):
        e = event.Event.for_name("Drink glass of water")
        o = e.track(when=datetime(2014, 1, 1, 16, 6, 20, 216238))
        self.assertEqual(str(o), "Jan 01, 2014 04:06PM")
        o = e.track(when=datetime(2015, 3, 2, 0, 34, 53, 327128))
        self.assertEqual(str(o), "Mar 02, 2015 12:34AM")

    def test_list_events(self):
        e1 = event.Event.for_name("Drink glass of water")
        e2 = event.Event.for_name("Clean litter box")

        self.assertEqual(event.Event.all(), [e2, e1])

    def test_alternate_time(self):
        e = event.Event.for_name("Drink glass of water")
        o = e.track()
        self.assertDatetimesEqual(o.when, datetime.now())

        when = earlier(hours=10)
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

    def test_slug(self):
        e = event.Event.for_name("Drink glass of water")
        self.assertEqual(e.slug, "Drink_glass_of_water")

    def test_exports_csv(self):
        e = event.Event.for_name("Drink glass of water")
        o = e.track(when=earlier(seconds=-1), attrs=dict(size="16", location="office"))
        e.track(attrs=dict(hello="world", when="now"))
        e.track(attrs=dict(hello="goodbye", location="office"))
        Session.commit()
        csv_file = list(csv.reader(e.export_csv().splitlines()))
        self.assertEqual(csv_file[0], ["When", "hello", "location", "size", "when"])
        self.assertEqual(csv_file[1], [str(o.when), "", "office", "16", ""])
        self.assertEqual(len(csv_file), 4)


def earlier(**kwargs):
    return datetime.now() - timedelta(**kwargs)
