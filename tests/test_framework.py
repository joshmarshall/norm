"""Test Norm interfaces."""

from unittest import TestCase
import norm.framework


class TestFramework(TestCase):

    def assert_requires_methods(
            self, interface, methods, exception, customize=lambda x: x):
        for skip_method in methods:
            model_methods = dict([
                (method, lambda self: None)
                for method in methods
                if method != skip_method
            ])
            customize(model_methods)

            with self.assertRaises(exception):
                interface(type("Implementation", (object,), model_methods))

    def test_model_requires_methods(self):
        self.assert_requires_methods(
            norm.framework.model, ["identify", "from_dict", "to_dict"],
            norm.framework.InvalidModel)

    def test_model_implementation(self):

        @norm.framework.model
        class Model(object):

            def identify(self):
                pass

            def to_dict(self):
                pass

            @classmethod
            def from_dict(self):
                pass

    def test_store_requires_methods(self):

        def customize(attributes):
            save = attributes.get("save", None)
            fetch = attributes.get("fetch", None)
            if save:
                save._NORM_SERIALIZE = True
            if fetch:
                fetch._NORM_DESERIALIZE = True

        self.assert_requires_methods(
            norm.framework.store, ["save", "fetch"],
            norm.framework.InvalidStore, customize)

    def test_missing_serialization(self):
        methods = {
            "save": lambda x: x,
            "fetch": classmethod(lambda x: x)
        }
        with self.assertRaises(norm.framework.InvalidStore):
            norm.framework.store(type("Store", (object,), methods))

    def test_store_implementation(self):

        @norm.framework.store
        class Store(object):

            @norm.framework.deserialize
            def fetch(self, key, factory):
                pass

            @norm.framework.serialize
            def save(self, instance):
                pass

    def test_connection_requires_methods(self):
        self.assert_requires_methods(
            norm.framework.connection,
            ["from_uri", "disconnect", "get_store"],
            norm.framework.InvalidConnection)

    def test_connection_implementation(self):

        @norm.framework.connection
        class Connection(object):

            @classmethod
            def from_uri(self, uri):
                pass

            def disconnect(self):
                pass

            def get_store(self):
                pass

    def test_serialize(self):
        foo = lambda x: None
        foo = norm.framework.serialize(foo)
        self.assertEqual(True, foo._NORM_SERIALIZE)

    def test_deserialize(self):
        foo = lambda x: None
        foo = norm.framework.deserialize(foo)
        self.assertEqual(True, foo._NORM_DESERIALIZE)

    def test_cannot_serialize_and_deserialize(self):
        foo = lambda x: None
        foo = norm.framework.deserialize(foo)
        with self.assertRaises(norm.framework.InterfaceMismatch):
            norm.framework.serialize(foo)

        foo = lambda x: None
        foo = norm.framework.serialize(foo)
        with self.assertRaises(norm.framework.InterfaceMismatch):
            norm.framework.deserialize(foo)
