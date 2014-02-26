class Field(object):

    def __init__(
            self, valid_type=None, default=None, coerce=lambda x: x,
            serialize=lambda x: x, deserialize=lambda x: x):
        self._default = default
        self._coerce = coerce
        self._serialize = serialize
        self._deserialize = deserialize
        self._valid_type = valid_type

    def __set__(self, obj, value):
        field_name = get_field_name(obj.__class__, self)
        value = self._coerce(value)
        if self._valid_type is not None and not \
                isinstance(value, self._valid_type):
            raise TypeError(
                "Invalid type `{}` for field `{}`".format(
                    type(value), field_name))
        obj.fields[field_name] = self._serialize(value)

    def __get__(self, obj, objtype):
        field_name = get_field_name(objtype, self)
        value = obj.fields.setdefault(field_name, self._default)
        return self._deserialize(value)


def get_field_name(cls, field):
    for attr in cls.__dict__:
        if cls.__dict__[attr] == field:
            return attr
    raise Exception("what?")
