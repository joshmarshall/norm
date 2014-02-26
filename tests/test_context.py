"""Test the norm master context object."""

from mock import Mock

from norm.context import Context, StoreContext, StoreContextWrapper

from unittest2 import TestCase


class Base(object):

    def __init__(self, **kwargs):
        self.data = kwargs

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return self.data

    def identify(self, key=None):
        if key:
            self.data["id"] = key
        return self.data.get("id")


class TestNormContext(TestCase):

    def setUp(self):
        self._context = Context()
        self._mock_connection = Mock()
        self._mock_connection2 = Mock()
        self._context.register_connection("mock", self._mock_connection)
        self._context.register_connection("mock2", self._mock_connection2)

    def test_context_register_connection(self):
        self._context.get_connection("mock://host")
        self._mock_connection.from_uri.assert_called_with("mock://host")
        self._context.get_connection("mock2://host")
        self._mock_connection2.from_uri.assert_called_with("mock2://host")

    def test_store_context_descriptor(self):
        mock_store = Mock()
        mock_store.fetch._NORM_DESERIALIZE = True
        mock_store.save._NORM_SERIALIZE = True

        class Model(Base):
            store = StoreContext(mock_store)

        result = Model.store.fetch("foobar")
        mock_store.fetch.assert_called_with(Model, "foobar")
        self.assertEqual(result, mock_store.fetch.return_value)

        model = Model(id="foobar", foo="bar")
        result = model.store.save()
        mock_store.save.assert_called_with(model)
        self.assertEqual(result, mock_store.save.return_value)

    def test_store_context_model_mismatch(self):
        mock_store = Mock()

        class Model(Base):
            store = StoreContext(mock_store)

        with self.assertRaises(AttributeError):
            Model.store.fetch()

        with self.assertRaises(AttributeError):
            Model().store.save()

    def test_store_context_wrapper(self):
        mock_store = Mock()
        mock_store.fetch._NORM_DESERIALIZE = True
        mock_store.save._NORM_SERIALIZE = True

        class Model(Base):
            use = StoreContextWrapper()

        M = Model.use(mock_store)
        M.store.fetch("foobar")
        mock_store.fetch.assert_called_with(M, "foobar")

        m = M()
        m.store.save()
        mock_store.save.assert_called_with(m)
