# Right now, defaults to an EMPTY field unless explicitly set to a "sane"
# None / null value. This is more friendly to document / KV stores than to
# column-based stores.

from collections import namedtuple


EMPTY = namedtuple("EmptyField", [])()


class Field(object):

    def __init__(
            self, valid_type=None, default=EMPTY, coerce=lambda x: x,
            serialize=lambda x, y: y, deserialize=lambda x, y: y,
            field_name=None, required=False):

        # public attributes
        self.default = default
        self.required = required

        # private attributes / functions
        self._coerce = coerce
        self._serialize = serialize
        self._deserialize = deserialize
        self._valid_type = valid_type
        self._field_name = field_name

    def set_default(self, field_name, instance):
        if callable(self.default):
            value = self.default()
        else:
            value = self.default
        if value is not EMPTY and value is not None:
            value = self._serialize(instance, value)
        if value is not EMPTY:
            instance[field_name] = value
        return value

    def __set__(self, obj, value):
        field_name = self._get_field_name(obj.__class__)
        value = self._coerce(value)
        if self._valid_type is not None and not \
                isinstance(value, self._valid_type):
            raise TypeError(
                "Invalid type `{}` for field `{}`".format(
                    type(value), field_name))
        if value is not None:
            value = self._serialize(obj, value)
        obj[field_name] = value

    def __get__(self, obj, objtype):
        if obj is None:
            return self
        field_name = self._get_field_name(objtype)
        try:
            value = obj[field_name]
        except KeyError:
            value = self.set_default(field_name, obj)

        if value is EMPTY:
            if self.required:
                raise EmptyRequiredField(
                    "Field '{0}' on model '{1}' is empty but required.".format(
                        field_name, obj.__class__.__name__))
            # there's an option to raise an explicit EmptyField error
            # here. that seems a bit unfriendly to document stores...
            # however this interface keeps us from knowing the difference
            # between an unset field and an explicit NULL value.
            value = None

        if value is not None:
            value = self._deserialize(obj, value)
        return value

    def _get_field_name(self, cls):
        if not hasattr(self, "__field_name"):
            self.__field_name = self._field_name or get_field_name(cls, self)
        return self.__field_name


def get_field_name(cls, field):
    for attr in dir(cls):
        if attr.startswith("_"):
            continue
        if getattr(cls, attr) is field:
            return attr
    raise AttributeError(
        "No field found on model {}".format(cls.__name__))


def get_all_fields(cls):
    for attr in dir(cls):
        field = getattr(cls, attr)
        if isinstance(field, Field):
            yield attr, field


def get_all_field_names(cls):
    return [f for f, _ in get_all_fields(cls)]


def populate_defaults(model):
    model_class = model.__class__
    for field_name in get_all_field_names(model_class):
        field = getattr(model_class, field_name)
        field.set_default(field_name, model)


class EmptyRequiredField(Exception):
    pass
