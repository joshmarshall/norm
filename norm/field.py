class Field(object):

    def __init__(
            self, valid_type=None, default=None, coerce=lambda x: x,
            serialize=lambda x: x, deserialize=lambda x: x,
            field_name=None):
        self._default = default
        self._coerce = coerce
        self._serialize = serialize
        self._deserialize = deserialize
        self._valid_type = valid_type
        self._field_name = field_name

    def set_default(self, field_name, instance):
        if callable(self._default):
            value = self._default()
        else:
            value = self._default
        if self._default:
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
            value = self._serialize(value)
        obj[field_name] = value

    def __get__(self, obj, objtype):
        if obj is None:
            return self
        field_name = self._get_field_name(objtype)
        try:
            value = obj[field_name]
        except KeyError:
            value = self.set_default(field_name, obj)
        if value is not None:
            value = self._deserialize(value)
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


def get_all_field_names(cls):
    fields = []
    for attr in dir(cls):
        if isinstance(getattr(cls, attr), Field):
            fields.append(attr)
    return fields


def populate_defaults(model):
    model_class = model.__class__
    for field_name in get_all_field_names(model_class):
        field = getattr(model_class, field_name)
        field.set_default(field_name, model)
