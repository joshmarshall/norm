import norm.framework
from norm.context import StoreContextWrapper
from norm.field import populate_defaults, get_all_field_names


@norm.framework.model
class Model(object):

    _id_field = "id"

    use = StoreContextWrapper()

    def __new__(cls, *args, **kwargs):
        instance = super(Model, cls).__new__(cls)
        instance._data = {}
        populate_defaults(instance)
        return instance

    def __init__(self, **kwargs):
        # intented to be overwritten on all but the most simple models
        field_names = get_all_field_names(self.__class__)
        for field, value in kwargs.items():
            if field not in field_names:
                raise UnknownField(
                    "Could not set field '{0}' on model '{1}'".format(
                        field, self.__class__.__name__))
            setattr(self, field, value)

    @classmethod
    def from_dict(cls, data):
        result = cls.__new__(cls)
        result._data.update(data)
        return result

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def to_dict(self):
        return self._data

    def identify(self, identifier=None):
        if not hasattr(self, self._id_field):
            raise MissingIDField(
                "Model `{}` is configured to use an id field named `{}`, "
                "but does not implement one.".format(
                    self.__class__.__name__, self._id_field))
        if identifier:
            self._data[self._id_field] = identifier
        return getattr(self, self._id_field)

    def __eq__(self, other):
        return self.identify() == other.identify() and \
            self.__class__.__name__ == other.__class__.__name__


class MissingIDField(Exception):
    """
    Raised when identify() is called on a Model that doesn't implement
    an id attribute on the model class.

    """
    pass


class UnknownField(Exception):
    """
    Raised when an unknown field is passed into construction.

    """
    pass
