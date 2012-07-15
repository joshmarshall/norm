"""Test the norm master context object."""

from mock import Mock

from norm.context import Context

from unittest2 import TestCase

class TestNormContext(TestCase):

    def setUp(self):
        self._context = Context()
        self._mock_connection = Mock()
        self._mock_store = Mock()
        self._context.register_connection("mock", self._mock_connection)
        self._context.register_store("mock", self._mock_store)

    def test_context_register_connection(self):
        self._context.get_connection("mock://host")
        self._mock_connection.from_uri.assert_called_with("mock://host")

    def test_context_register_store(self):
        self._context.get_store("mock", self._mock_connection, foo="bar")
        self._mock_store.assert_called_with(self._mock_connection, foo="bar")

    def test_context_wrapper(self):
        connection = self._context.get_connection("mock://host")
        connection.get_store(foo="bar")
        self._mock_store.assert_called_with(connection._connection, foo="bar")
