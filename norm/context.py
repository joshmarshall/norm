"""
The Context class. This is used to register backend connections and stores.
"""

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from norm.framework import _deserializable, _serializable


class Context(object):

    def __init__(self):
        self._connection_classes = {}

    def register_connection(self, name, connection_class):
        self._connection_classes[name] = connection_class

    def get_connection(self, connection_uri):
        parsed = urlparse.urlparse(connection_uri)
        connection_type_name = parsed.scheme
        connection_type = self._connection_classes[connection_type_name]
        return connection_type.from_uri(connection_uri)


class StoreContext(object):

    def __init__(self, store):
        self._store = store

    def __get__(self, obj, objtype):
        return _StoreContextAttribute(self._store, obj, objtype)


class _StoreContextAttribute(object):

    def __init__(self, store, instance, model):
        self._store = store
        self._instance = instance
        self._model = model

    def __getattr__(self, attribute_name):
        attribute = getattr(self._store, attribute_name)
        if self._instance:
            return self._instance_attribute(attribute, attribute_name)
        return self._model_attribute(attribute, attribute_name)

    def _instance_attribute(self, attribute, attribute_name):
        if _deserializable(attribute):
            def call(*args, **kwargs):
                return attribute(self._instance.__class__, *args, **kwargs)
            return call
        elif _serializable(attribute):
            def call(*args, **kwargs):
                return attribute(self._instance, *args, **kwargs)
            return call
        else:
            raise AttributeError(
                "Attribute `{}` not available for instances on "
                "store `{}`.".format(attribute_name, self._store.__class__))

    def _model_attribute(self, attribute, attribute_name):
        if not _deserializable(attribute):
            raise AttributeError(
                "Attribute `{}` not available for models on "
                "store `{}`.".format(attribute_name, self._store.__class__))

        def call(*args, **kwargs):
            return attribute(self._model, *args, **kwargs)
        return call


class StoreContextWrapper(object):

    def __init__(self):
        self._model = None

    def __get__(self, obj, objtype):
        def wrap_model(store):
            # one could argue that we want to pass in the original objtype
            # here instead of using the descriptor lookup in StoreContext,
            # but the usability limitation of that seems less desirable.
            return type(
                objtype.__name__, (objtype,), {"store": StoreContext(store)})
        return wrap_model
