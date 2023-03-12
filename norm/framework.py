from typing import (
    Any,
    cast,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    Type,
    TypeVar,
    runtime_checkable,
)


class InterfaceMismatch(Exception):
    pass


class InvalidModel(Exception):
    pass


class InvalidStore(Exception):
    pass


class InvalidConnection(Exception):
    pass


ID = TypeVar("ID")
M = TypeVar("M")


@runtime_checkable
class ModelSerializer(Protocol[ID]):
    def to_dict(self) -> MutableMapping[str, Any]:
        ...

    def identify(self, key: Optional[ID] = None) -> ID:
        ...

    @classmethod
    def from_dict(cls: Type[M], data: Mapping[str, Any]) -> M:
        ...


@runtime_checkable
class Store(Protocol):
    def fetch(self, model: Type[M], key: ID) -> Optional[M]:
        ...

    def save(self, instance: M) -> None:
        ...

    def delete(self, model: M, key: ID) -> None:
        ...


S = TypeVar("S", covariant=True)
C = TypeVar("C")


@runtime_checkable
class Connection(Protocol[S]):
    @classmethod
    def from_uri(cls: Type[C], uri: str) -> C:
        ...

    def disconnect(self) -> None:
        ...

    def get_store(self) -> S:
        ...


def model(cls: Type[M]) -> Type[M]:
    try:
        assert issubclass(cls, ModelSerializer)
    except AssertionError as exc:
        raise InvalidModel(str(exc)) from exc
    return cast(Type[M], cls)


def connection(cls: Type[C]) -> Type[C]:
    try:
        assert issubclass(cls, Connection)
    except AssertionError as exc:
        raise InvalidConnection(str(exc)) from exc
    return cast(Type[C], cls)


def store(cls: Type[S]) -> Type[S]:
    try:
        assert issubclass(cls, Store)
    except AssertionError as exc:
        raise InvalidStore(str(exc)) from exc

    if not _serializable(cls.save):
        raise InvalidStore(
            "`{}.save` must be serializable.".format(cls.__name__))
    if not _deserializable(cls.fetch):
        raise InvalidStore(
            "`{}.fetch` must be deserializable.".format(cls.__name__))

    return cast(Type[S], cls)


def _check_existing_serialization(attribute: Any) -> None:
    if _serializable(attribute) or _deserializable(attribute):
        raise InterfaceMismatch(
            "Cannot set multiple values for serialization and deserialization "
            "on the same attribute `{}`.".format(attribute)
        )


A = TypeVar("A")


def serialize(attribute: A) -> A:
    _check_existing_serialization(attribute)
    setattr(attribute, "_NORM_SERIALIZE", True)
    return attribute


def deserialize(attribute: A) -> A:
    _check_existing_serialization(attribute)
    setattr(attribute, "_NORM_DESERIALIZE", True)
    return attribute


def _deserializable(attribute: A) -> bool:
    return getattr(attribute, "_NORM_DESERIALIZE", False) is True


def _serializable(attribute: A) -> bool:
    return getattr(attribute, "_NORM_SERIALIZE", False) is True
