import norm.framework
from norm.context import StoreContextWrapper
from norm.field import populate_defaults, get_all_fields, EmptyRequiredField


@norm.framework.model
class Model(object):

    _id_field = "id"

    use = StoreContextWrapper()

    def __new__(cls, *args, **kwargs):
        # caching fields and required fields on the model
        # so we don't have to discover every time.
        if not hasattr(cls, "_fields"):
            fields = []
            required_fields = []
            for field_name, field in get_all_fields(cls):
                fields.append(field_name)
                if field.required:
                    required_fields.append(field_name)
            cls._fields = set(fields)
            cls._required_fields = set(required_fields)

        instance = super(Model, cls).__new__(cls)
        instance._data = {}
        populate_defaults(instance)
        return instance

    def __init__(self, **kwargs):
        # intented to be overwritten on all but the most simple models
        # currently implements two things: invalid field checking and
        # required field checking. custom models can implement this logic
        # however they want, no need to even call super()
        model_name = self.__class__.__name__
        missing_keys = self._required_fields.difference(
            list(kwargs.keys()) + list(self._data.keys()))
        if missing_keys:
            raise EmptyRequiredField(
                "Field(s) ('{0}') for model '{1}' is "
                "required but empty.".format(
                    "', '".join(missing_keys), model_name))

        if not self._fields.issuperset(kwargs.keys()):
            unknown_fields = set(kwargs.keys()).difference(self._fields)
            raise UnknownField(
                "Could not set field(s) ('{0}') on model '{1}'".format(
                    "', '".join(unknown_fields), model_name))

        for field, value in kwargs.items():
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

    def identify(self, key=None):
        if not hasattr(self, self._id_field):
            raise MissingIDField(
                "Model `{}` is configured to use an id field named `{}`, "
                "but does not implement one.".format(
                    self.__class__.__name__, self._id_field))
        if key:
            self._data[self._id_field] = key
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
    pass
