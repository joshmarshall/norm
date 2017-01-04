"""Just a general placeholder for usage tests for now."""

import dbm
import json
import os
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

    def identify(self, key=None):
        return self._uid

    def __eq__(self, other):
        return self.identify() == other.identify()


class TestDBMBackend(TestCase):

    def setUp(self):
        with tempfile.NamedTemporaryFile(suffix=".db") as temp:
            self._tempfile = temp.name
        self._connection = dbm_backend.DBMConnection(self._tempfile)
        self._store = dbm_backend.DBMStore(self._connection)
        self._person = Person(name="Foobar", uid="foobar")

    def tearDown(self):
        if os.path.exists(self._tempfile):
            os.remove(self._tempfile)

    def test_save(self):
        self._store.save(self._person)
        dbm_connection = dbm.open(self._tempfile, "r")
        self.assertEqual(
            {"name": "Foobar", "uid": "foobar"},
            json.loads(dbm_connection["Person:foobar"].decode("utf8")))

    def test_fetch(self):
        self._store.save(self._person)
        fetched = self._store.fetch(Person, "foobar")
        self.assertEqual(fetched, self._person)

    def test_fetch_none(self):
        fetched = self._store.fetch(Person, "whatever")
        self.assertIsNone(fetched)

    def test_register(self):
        context = Context()
        dbm_backend.register(context)
        self._store.save(self._person)

        # creating a different connection to test...
        connection = context.get_connection("dbm://%s" % self._tempfile)
        store = connection.get_store()
        person = store.fetch(Person, "foobar")
        self.assertEqual(person, self._person)

    def test_create(self):
        person = self._store.create(Person, name="Foo Bar", uid="foobar")
        self.assertEqual(
            {"uid": "foobar", "name": "Foo Bar"}, person.to_dict())

        person2 = self._store.fetch(Person, "foobar")
        self.assertEqual(person.to_dict(), person2.to_dict())

    def test_find(self):
        persons = []
        for i in range(10):
            person = self._store.create(Person, name=str(i), uid=str(i))
            persons.append(person.identify())

        actual_persons = []
        for person in self._store.find(Person):
            actual_persons.append(person.identify())

        for person in persons:
            self.assertTrue(person in actual_persons)

    def test_delete(self):
        for i in range(10):
            person = self._store.create(Person, name=str(i), uid=str(i))
        self._store.delete(Person, person.identify())
        people = list(self._store.find(Person))
        self.assertEqual(9, len(people))
        uids = [p.identify() for p in people]
        self.assertFalse(person.identify() in uids)
