"""Interfaces for various Norm classes."""

import interfaces

class InvalidModel(Exception):
    """Raised when a model does not implement the required methods."""
    pass

class InvalidStore(Exception):
    """Raised when a store does not implement the required methods."""
    pass

class InvalidConnection(Exception):
    """Raised when a connection does not implement the required methods."""
    pass

def model(cls):
    try:
        return interfaces.implement(Model)(cls)
    except interfaces.MissingRequiredAttribute, exc:
        raise InvalidModel("%s" % exc)

def store(cls):
    try:
        return interfaces.implement(Store)(cls)
    except interfaces.MissingRequiredAttribute, exc:
        raise InvalidStore("%s" % exc)

def connection(cls):
    try:
        return interfaces.implement(Connection)(cls)
    except interfaces.MissingRequiredAttribute, exc:
        raise InvalidConnection("%s" % exc)
    except interfaces.MissingRequiredClassMethod, exc:
        raise InvalidConnection("%s" % exc)


@interfaces.define
class Model(object):

    @interfaces.require
    def dictify(self):
        """All models must implement a `dictify(self)` method."""
        pass

    @interfaces.require
    def get_key(self):
        """All models must implement a `get_key(self)` method."""
        pass


@interfaces.define
class Store(object):

    @interfaces.require
    def fetch(self, key, factory):
        """All stores must implement a `fetch(self, key, factory)` method."""
        pass

    @interfaces.require
    def save(self, instance):
        """All stores must implement a `save(self, instance)` method."""
        pass

@interfaces.define
class Connection(object):

    @interfaces.require
    def save(self, key, data):
        """All connections must implement a `save(self, key, data)` method."""
        pass

    @interfaces.require
    def connect(self):
        """All connections must implement a `connect(self)` method."""
        pass

    @interfaces.require
    def fetch(self, key):
        """All connections must implement a `fetch(self)` method."""
        pass

    @interfaces.require_classmethod
    def from_uri(cls, uri):
        """
        All connections must implement a `from_uri(cls, uri)` classmethod.

        """
        pass
