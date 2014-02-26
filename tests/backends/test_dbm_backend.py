"""Just a general placeholder for usage tests for now."""

import dbm
import json
import tempfile
from unittest2 import TestCase

from norm.backends import dbm_backend
from norm.context import Context
import norm.framework


@norm.framework.model
class Person(object):

    def __init__(self, name, uid):
        self._name = name
        self._uid = uid

    def to_dict(self):
        return {
            "name": self._name,
            "uid": self._uid
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def identify(self):
        return self._uid

    def __eq__(self, other):
        return self.identify() == other.identify()


class TestDBMBackend(TestCase):

    def setUp(self):
        self._tempfile = tempfile.NamedTemporaryFile(suffix=".db")
        self._connection = dbm_backend.DBMConnection(self._tempfile.name)
        self._connection.connect()
        self._store = dbm_backend.DBMStore(self._connection)
        self._person = Person(name="Foobar", uid="foobar")

    def tearDown(self):
        self._tempfile.close()

    def test_save(self):
        self._store.save(self._person)
        dbm_connection = dbm.open(self._tempfile.name, "r")
        self.assertEqual(
            {"name": "Foobar", "uid": "foobar"},
            json.loads(dbm_connection["Person:foobar"]))

    def test_fetch(self):
        self._store.save(self._person)
        fetched = self._store.fetch(Person, "foobar")
        self.assertEqual(fetched, self._person)

    def test_register(self):
        context = Context()
        dbm_backend.register(context)
        self._store.save(self._person)

        # creating a different connection to test...
        connection = context.get_connection("dbm://%s" % self._tempfile.name)
        connection.connect()
        store = connection.get_store()
        person = store.fetch(Person, "foobar")
        self.assertEqual(person, self._person)
