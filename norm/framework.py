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


def _interface_validator(interface, exception):
    def validate(cls):
        try:
            return interfaces.implement(interface)(cls)
        except (
                interfaces.MissingRequiredMethod,
                interfaces.MissingRequiredClassMethod
        ) as exc:
            error_string = "Error in class `{}`: {}".format(cls.__name__, exc)
            raise exception(error_string)
    return validate


@interfaces.define
class ModelInterface(object):

    @interfaces.require
    def to_dict(self):
        """All models must implement: `to_dict()`"""
        pass

    @interfaces.require
    def identify(self, key=None):
        """All models must implement: `identify()`"""
        pass

    @interfaces.require_classmethod
    def from_dict(self, data):
        """All models must implement: `from_dict()`"""
        pass


@interfaces.define
class StoreInterface(object):

    @interfaces.require
    def fetch(self, model, key):
        """All stores must implement: `fetch()`"""
        pass

    @interfaces.require
    def save(self, instance):
        """All stores must implement: `save()`"""
        pass

    @interfaces.require
    def delete(self, model, key):
        """All stores must implement: `delete()`"""
        pass


@interfaces.define
class ConnectionInterface(object):

    @interfaces.require_classmethod
    def from_uri(cls, uri):
        """All connections must implement: `from_uri()`"""
        pass

    @interfaces.require
    def disconnect(self):
        """All connections must implement: `disconnect()`"""
        pass

    @interfaces.require
    def get_store(self):
        """All connections must implement: `get_store()`"""
        pass


# helper classmethods for implementing interfaces...
model = _interface_validator(ModelInterface, InvalidModel)
connection = _interface_validator(ConnectionInterface, InvalidConnection)


def store(cls):
    cls = _interface_validator(StoreInterface, InvalidStore)(cls)
    if not _serializable(cls.save):
        raise InvalidStore(
            "`{}.save` must be serializable.".format(cls.__name__))
    if not _deserializable(cls.fetch):
        raise InvalidStore(
            "`{}.fetch` must be deserializable.".format(cls.__name__))
    return cls


def _check_existing_serialization(attribute):
    if getattr(attribute, "_NORM_SERIALIZE", False) is True or \
            getattr(attribute, "_NORM_DESERIALIZE", False) is True:
        raise InterfaceMismatch(
            "Cannot set multiple values for serialization and deserialization "
            "on the same attribute `{}`.".format(attribute))


def serialize(attribute):
    _check_existing_serialization(attribute)
    attribute._NORM_SERIALIZE = True
    return attribute


def deserialize(attribute):
    _check_existing_serialization(attribute)
    attribute._NORM_DESERIALIZE = True
    return attribute


def _deserializable(attribute):
    return getattr(attribute, "_NORM_DESERIALIZE", False) is True


def _serializable(attribute):
    return getattr(attribute, "_NORM_SERIALIZE", False) is True


class InterfaceMismatch(Exception):
    """Raised when both serialization and deserialization are enabled."""
    pass
