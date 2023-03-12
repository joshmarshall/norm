# Right now, defaults to an EMPTY field unless explicitly set to a "sane"
# None / null value. This is more friendly to document / KV stores than to
# column-based stores.

from enum import Enum
from typing import (
    Any, cast, Callable, Final, Iterator, List,
    Literal, Generic, overload, Protocol, Tuple, Type, TypeVar
)


class Sentinel(Enum):
    EMPTY = 0


EMPTY: Final = Sentinel.EMPTY
EmptyType = Literal[Sentinel.EMPTY]


class M(Protocol):

    def __getitem__(self, key: str) -> Any:
        ...

    def __setitem__(self, key: str, value: Any) -> None:
        ...


D = TypeVar("D")
T = TypeVar("T")


Coerce = Callable[[Any], D]
Serialize = Callable[[M, D], Any]
Deserialize = Callable[[M, Any], D]
Default = Callable[[], D]


class Field(Generic[D]):

    __coerce: None | Coerce[D]
    __serialize: None | Serialize[D]
    __deserialize: None | Deserialize[D]

    def __init__(
        self,
        valid_type: None | Type[D] = None,
        default: EmptyType | D | Default[D] = EMPTY,
        coerce: None | Coerce[D] = None,
        serialize: None | Serialize[D] = None,
        deserialize: None | Deserialize[D] = None,
        field_name: str | None = None,
        required: bool = False,
    ) -> None:
        # public attributes
        self.default = default
        self.required = required
        self._valid_type: type = valid_type if valid_type is not None else object
        self._field_name = field_name
        self.__coerce = coerce
        self.__serialize = serialize
        self.__deserialize = deserialize

    def _coerce(self, val: Any) -> D:
        if self.__coerce is not None:
            return self.__coerce(val)

        if self._valid_type is not None and not isinstance(val, self._valid_type):
            raise TypeError(
                "Invalid value `{}` for field `{}`".format(val, self._field_name)
            )
        return cast(D, val)

    def _serialize(self, instance: M, val: D) -> Any:
        if val is not None and self.__serialize is not None:
            return self.__serialize(instance, val)
        return val

    def _deserialize(self, instance: M, val: Any) -> D:
        if self.__deserialize is not None:
            return self.__deserialize(instance, val)
        return cast(D, val)

    def set_default(self, field_name: str, instance: M) -> EmptyType | D:
        value: EmptyType | D
        if callable(self.default):
            value = self.default()
        else:
            value = self.default
        if value == EMPTY:
            return EMPTY
        instance[field_name] = self._serialize(instance, value)
        return value

    def __set__(self, obj: M, value: D) -> None:
        field_name = self._get_field_name(obj.__class__)
        coerced_value = self._coerce(value)
        obj[field_name] = self._serialize(obj, coerced_value)

    @overload
    def __get__(self, obj: None, objtype: type) -> "Field[D]":
        ...

    @overload
    def __get__(self, obj: M, objtype: None) -> D | None:
        ...

    def __get__(self, obj: M | None, objtype: None | type) -> "Field[D]" | D | None:
        if obj is None:
            return self

        field_name = self._get_field_name(obj.__class__)

        try:
            value = self._deserialize(obj, obj[field_name])
        except KeyError:
            default_value = self.set_default(field_name, obj)

            if default_value is EMPTY:
                if self.required:
                    raise EmptyRequiredField(
                        "Field '{0}' on model '{1}' is empty but required.".format(
                            field_name, obj.__class__.__name__
                        )
                    )
                # there's an option to raise an explicit EmptyField error
                # here. that seems a bit unfriendly to document stores...
                # however this interface keeps us from knowing the difference
                # between an unset field and an explicit NULL value.
                value = None
            else:
                value = default_value

        return value

    def _get_field_name(self, cls: Type[Any]) -> str:
        if not hasattr(self, "__field_name"):
            self.__field_name = self._field_name or get_field_name(cls, self)
        return self.__field_name


def get_field_name(cls: Type[Any], field: Field[Any]) -> str:
    for attr in dir(cls):
        if attr.startswith("_"):
            continue
        if getattr(cls, attr) is field:
            return attr
    raise AttributeError("No field found on model {}".format(cls.__name__))


def get_all_fields(cls: Type[Any]) -> Iterator[Tuple[str, Field[Any]]]:
    for attr in dir(cls):
        field = getattr(cls, attr)
        if isinstance(field, Field):
            yield attr, field


def get_all_field_names(cls: Type[Any]) -> List[str]:
    return [f for f, _ in get_all_fields(cls)]


def populate_defaults(model: M) -> None:
    model_class = model.__class__
    for field_name in get_all_field_names(model_class):
        field = getattr(model_class, field_name)
        field.set_default(field_name, model)


class EmptyRequiredField(Exception):
    pass
