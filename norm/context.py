"""
The Context class. This is used to register backend connections and stores.
"""

import urllib.parse
from typing import Any, Callable, cast, Dict, Generic, overload, Type, TypeVar

from norm.framework import Connection, Store, _deserializable, _serializable

M = TypeVar("M")
S = TypeVar("S")
C = TypeVar("C")


class Context:
    def __init__(self) -> None:
        self._connection_classes: Dict[str, Type[Connection[Any]]] = {}

    def register_connection(
        self, name: str, connection_class: Type[Connection[Any]]
    ) -> None:
        self._connection_classes[name] = connection_class

    def get_connection(self, connection_uri: str) -> Connection[Any]:
        parsed = urllib.parse.urlparse(connection_uri)
        connection_type_name = parsed.scheme
        connection_type = self._connection_classes[connection_type_name]
        return connection_type.from_uri(connection_uri)


class _StoreInstanceAttribute(Generic[M]):
    def __init__(self, store: Store, instance: M) -> None:
        self._store = store
        self._instance = instance
        self._model = instance.__class__

    def __getattr__(
        self, attribute_name: str
    ) -> Callable[..., Any]:
        attribute = getattr(self._store, attribute_name)
        if not callable(attribute):
            raise AttributeError(
                f"Attribute `{attribute_name}` not available for instances on "
                f"store `{self._store.__class__}`."
            )

        if _serializable(attribute):
            def call(*args: Any, **kwargs: Any) -> Any:
                return attribute(self._instance, *args, **kwargs)
            return call
        elif _deserializable(attribute):
            def call(*args: Any, **kwargs: Any) -> Any:
                # based on the signature of _deserializable, should be a
                # safe cast since getattr won't help with that
                return attribute(self._model, *args, **kwargs)
            return call
        else:
            raise AttributeError(
                f"Attribute `{attribute_name}` not available for instances on "
                f"store `{self._store.__class__}`."
            )


class _StoreClassAttribute(Generic[M]):
    def __init__(self, store: Store, model: Type[M]) -> None:
        self._store = store
        self._model = model

    def __getattr__(self, attribute_name: str) -> Callable[..., None | M]:
        attribute = getattr(self._store, attribute_name)
        if not callable(attribute):
            raise AttributeError(
                f"Attribute `{attribute_name}` not available for instances on "
                f"store `{self._store.__class__}`."
            )
        if _deserializable(attribute):
            def call(*args: Any, **kwargs: Any) -> None | M:
                # based on the signature of _deserializable, should be a
                # safe cast since getattr won't help with that
                return cast(M, attribute(self._model, *args, **kwargs))
            return call
        else:
            raise AttributeError(
                f"Attribute `{attribute_name}` not available for instances on "
                f"store `{self._store.__class__}`."
            )


class StoreContext(Generic[M]):
    def __init__(self, store: Store) -> None:
        self._store = store

    @overload
    def __get__(self, obj: None, objtype: Type[M]) -> _StoreClassAttribute[M]:
        ...

    @overload
    def __get__(self, obj: M) -> _StoreInstanceAttribute[M]:
        ...

    def __get__(
        self, obj: None | M, objtype: None | Type[M] = None
    ) -> _StoreClassAttribute[M] | _StoreInstanceAttribute[M]:
        if obj is not None:
            return _StoreInstanceAttribute(self._store, obj)
        elif objtype is not None:
            return _StoreClassAttribute(self._store, objtype)
        raise AttributeError(f"Store not available on {objtype}.")


class StoreContextWrapper:

    def __get__(
        self, obj: None | M, objtype: None | Type[M]
    ) -> Callable[[Store], StoreContext[M]]:
        cls = objtype if objtype is not None else obj.__class__

        def call(store: Store) -> StoreContext[M]:
            return cast(
                StoreContext[M],
                type(cls.__name__, (cls,), {"store": StoreContext(store)})
            )

        return call
