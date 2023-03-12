from unittest import TestCase
import norm.framework


class TestFramework(TestCase):

    def assert_requires_methods(
            self, interface, methods, exception, customize=lambda x: x):
        method_funcs = {
            "save": lambda self, instance: None,
            "delete": lambda self, model, key: None,
            "fetch": lambda self, model, key: None,
            "disconnect": lambda self: None,
            "from_dict": lambda self, data: None,
            "to_dict": lambda self: None,
            "identify": lambda self, key=None: None,
            "get_store": lambda self: None,
            "from_uri": lambda cls, uri: None
        }
        for skip_method in methods:
            model_methods = dict([
                (method, method_funcs[method])
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

            def identify(self, key=None):
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
            norm.framework.store, ["save", "fetch", "delete"],
            norm.framework.InvalidStore, customize)

    def test_missing_serialization(self):
        methods = {
            "save": lambda self, instance: None,
            "fetch": classmethod(lambda self, model, key: None),
            "delete": lambda self, model, key: None
        }
        with self.assertRaises(norm.framework.InvalidStore):
            norm.framework.store(type("Store", (object,), methods))

    def test_store_implementation(self):

        @norm.framework.store
        class Store(object):

            @norm.framework.deserialize
            def fetch(self, model, key):
                pass

            @norm.framework.serialize
            def save(self, instance):
                pass

            def delete(self, model, key):
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
        foo = norm.framework.serialize(lambda x: None)
        self.assertEqual(True, foo._NORM_SERIALIZE)

    def test_deserialize(self):
        foo = norm.framework.deserialize(lambda x: None)
        self.assertEqual(True, foo._NORM_DESERIALIZE)

    def test_cannot_serialize_and_deserialize(self):
        foo = norm.framework.deserialize(lambda x: None)
        with self.assertRaises(norm.framework.InterfaceMismatch):
            norm.framework.serialize(foo)

        foo = norm.framework.serialize(lambda x: None)
        with self.assertRaises(norm.framework.InterfaceMismatch):
            norm.framework.deserialize(foo)
