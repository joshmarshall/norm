"""
The Context class. This is used to register backend connections and stores.
"""

import urlparse

class Context(object):

    def __init__(self):
        self._connection_classes = {}
        self._store_classes = {}

    def register_connection(self, name, connection_class):
        self._connection_classes[name] = connection_class

    def register_store(self, name, store_class):
        self._store_classes[name] = store_class

    def get_store(self, store_name, connection, **kwargs):
        return self._store_classes[store_name](connection, **kwargs)

    def get_connection(self, connection_uri):
        parsed = urlparse.urlparse(connection_uri)
        connection_type_name = parsed.scheme
        connection_type = self._connection_classes[connection_type_name]
        connection = connection_type.from_uri(connection_uri)
        return _ConnectionWrapper(connection_type_name, self, connection)


class _ConnectionWrapper(object):
    """Provides a few shortcuts for connection <-> store."""

    def __init__(self, key, context, connection):
        self._key = key
        self._context = context
        self._connection = connection

    def __getattr__(self, attr):
        return getattr(self._connection, attr)

    def get_store(self, **kwargs):
        return self._context.get_store(self._key, self._connection, **kwargs)
