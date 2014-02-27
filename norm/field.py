class Field(object):

    def __init__(
            self, valid_type=None, default=None, coerce=lambda x: x,
            serialize=lambda x: x, deserialize=lambda x: x):
        self._default = default
        self._coerce = coerce
        self._serialize = serialize
        self._deserialize = deserialize
        self._valid_type = valid_type

    def set_default(self, field_name, model):
        if callable(self._default):
            value = self._default()
        else:
            value = self._default
        if self._default:
            model[field_name] = value
        return value

    def __set__(self, obj, value):
        field_name = get_field_name(obj.__class__, self)
        value = self._coerce(value)
        if self._valid_type is not None and not \
                isinstance(value, self._valid_type):
            raise TypeError(
                "Invalid type `{}` for field `{}`".format(
                    type(value), field_name))
        if value is not None:
            value = self._serialize(value)
        obj[field_name] = value

    def __get__(self, obj, objtype):
        field_name = get_field_name(objtype, self)
        try:
            value = obj[field_name]
        except KeyError:
            value = self.set_default(field_name, obj)
        if value is not None:
            value = self._deserialize(value)
        return value


def get_field_name(cls, field):
    for attr in cls.__dict__:
        if cls.__dict__[attr] == field:
            return attr
    raise AttributeError(
        "No field found on model {}".format(cls.__name__))


def get_all_field_names(cls):
    fields = []
    for attr in cls.__dict__:
        if isinstance(cls.__dict__[attr], Field):
            fields.append(attr)
    return fields


def populate_defaults(model):
    model_class = model.__class__
    for field_name in get_all_field_names(model_class):
        field = model_class.__dict__[field_name]
        field.set_default(field_name, model)
