"""Test a complete implementation of a fake backend."""

import unittest
import norm.framework
import norm.context


@norm.framework.connection
class FakeConnection(object):

    def __init__(self):
        self.data = {}

    def get_store(self):
        return FakeStore(self.data)

    @classmethod
    def from_uri(cls, uri):
        return cls()

    def disconnect(self):
        pass


@norm.framework.store
class FakeStore(object):

    def __init__(self, data):
        self._data = data

    @norm.framework.serialize
    def save(self, instance):
        model_name = instance.__class__.__name__
        instance_id = instance.identify()
        instance_data = instance.to_dict()
        self._data["{}.{}".format(model_name, instance_id)] = instance_data
        return instance_id

    @norm.framework.deserialize
    def fetch(self, model, key):
        model_name = model.__name__
        return self._data["{}.{}".format(model_name, key)]

    def delete(self, model, key):
        del self._data["{}.{}".format(model.__name__, key)]


@norm.framework.model
class Model(object):

    use = norm.context.StoreContextWrapper()

    def __init__(self, **kwargs):
        self.data = kwargs

    def to_dict(self):
        return self.data

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def identify(self, key=None):
        if key:
            self.data["id"] = key
        return self.data.get("id")


class TestFakeBackend(unittest.TestCase):

    def setUp(self):
        self._connection = FakeConnection()
        self._store = self._connection.get_store()

    def test_create(self):
        M = Model.use(self._store)
        foo = M(name="test", id="foo")
        foo.store.save()

        self.assertEqual(
            {"Model.foo": {"id": "foo", "name": "test"}},
            self._connection.data)
