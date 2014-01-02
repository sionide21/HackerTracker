import os
import unittest
from hackertracker import event
from hackertracker.database import Model, Session
from sqlalchemy import create_engine


# Need for tests
os.environ['AUTH_TOKEN'] = 'secr3t'


class TestEvents(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite:///:memory:', echo=True)
        Model.metadata.create_all(engine)
        Session.configure(bind=engine)
        import app  # Must be after Session is configured
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()

    def tearDown(self):
        Session.remove()

    def test_nothing_without_token(self):
        resp = self.app.post('/track/Run_the_unit_tests', data=dict(test="very yes"))
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Session.query(event.Event).count(), 0)
        self.assertEqual(Session.query(event.Event).count(), 0)
        self.assertEqual(Session.query(event.Attribute).count(), 0)

    def test_allows_header(self):
        resp = self.app.post('/track/Run_the_unit_tests', data=dict(test="very yes"), headers={"X-Auth-Token": "secr3t"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Session.query(event.Event).count(), 1)

    def test_allows_query_string(self):
        resp = self.app.post('/track/Run_the_unit_tests?auth=secr3t', data=dict(test="very yes"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Session.query(event.Event).count(), 1)
