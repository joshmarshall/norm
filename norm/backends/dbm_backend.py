"""Simple DBM interface for norm."""

import dbm
import json
from typing import Any, Iterator, Dict, Literal, Mapping, Type, TypeVar

from norm.context import Context
import norm.framework
from norm.framework import ModelSerializer


ID = TypeVar("ID")


@norm.framework.store
class DBMStore:
    def __init__(self, connection: "DBMConnection") -> None:
        self._connection = connection

    @norm.framework.deserialize
    def fetch(
        self, model: Type[ModelSerializer[ID]], key: ID
    ) -> None | ModelSerializer[ID]:
        values = self._fetch_values(model, key)
        if values is not None:
            return model.from_dict(values)
        return None

    def _fetch_values(
        self, model: Type[ModelSerializer[ID]], key: ID
    ) -> None | Dict[str, Any]:
        strkey = "%s:%s" % (model.__name__, key)
        byte_result = self._connection.fetch(strkey)
        if byte_result is None:
            return None
        result: Dict[str, Any] = json.loads(byte_result.decode("utf8"))
        return result

    @norm.framework.serialize
    def save(self, instance: ModelSerializer[Any]) -> None:
        ident = instance.identify()
        key: str = "%s:%s" % (instance.__class__.__name__, ident)
        data = instance.to_dict()
        self._connection.save(key, json.dumps(data).encode("utf8"))
        self._connection.flush()

    @norm.framework.deserialize
    def create(
        self, model: Type[ModelSerializer[Any]], **kwargs: Any
    ) -> ModelSerializer[Any]:
        instance = model(**kwargs)
        self.save(instance)
        return instance

    @norm.framework.deserialize
    def find(
        self, model: Type[ModelSerializer[Any]],
        query: None | Mapping[str, Any] = None
    ) -> Iterator[None | ModelSerializer[ID]]:
        prefix = "{}:".format(model.__name__)
        for key in self._connection.keys():
            if key.startswith(prefix):
                matched = True
                partial = key.split(prefix)[-1]
                values = self._fetch_values(model, partial)
                if values is None:
                    matched = False
                elif query is not None:
                    for key, value in query.items():
                        if values.get(key) != value:
                            matched = False
                            break
                if matched:
                    if values is None:
                        yield values
                    else:
                        yield model.from_dict(values)

    def delete(self, model: Type[ModelSerializer[ID]], key: ID) -> None:
        prefix = "{}:{}".format(model.__name__, key)
        self._connection.delete(prefix)


C = TypeVar("C", bound="DBMConnection")


@norm.framework.connection
class DBMConnection(object):
    @classmethod
    def from_uri(cls: Type[C], uri: str) -> C:
        path = uri.split("dbm://")[1]
        return cls(path)

    def __init__(self, path: str, flag: "Flag" = "c") -> None:
        self._path = path
        self._flag = flag
        self._open()

    def _open(self) -> None:
        self._dbm = dbm.open(self._path, self._flag)

    def disconnect(self) -> None:
        self._dbm.close()

    def get_store(self) -> DBMStore:
        return DBMStore(self)

    def keys(self) -> Iterator[str]:
        for raw_key in self._dbm.keys():
            if isinstance(raw_key, str):
                yield raw_key
            else:
                yield raw_key.decode("utf8")

    def flush(self) -> None:
        self._dbm.close()
        self._open()

    def save(self, key: str, data: bytes) -> None:
        self._dbm[key] = data

    def fetch(self, key: str) -> None | bytes:
        byte_key = key.encode("utf8")
        if byte_key not in self._dbm:
            return None
        return self._dbm[byte_key]

    def delete(self, key: str) -> None:
        del self._dbm[key]


def register(context: Context) -> None:
    context.register_connection("dbm", DBMConnection)


Flag = Literal[
    "r", "w", "c", "n", "rf", "wf", "cf", "nf", "rs", "ws", "cs", "ns", "ru",
    "wu", "cu", "nu", "rfs", "wfs", "cfs", "nfs", "rfu", "wfu", "cfu", "nfu",
    "rsf", "wsf", "csf", "nsf", "rsu", "wsu", "csu", "nsu", "ruf", "wuf",
    "cuf", "nuf", "rus", "wus", "cus", "nus", "rfsu", "wfsu", "cfsu", "nfsu",
    "rfus", "wfus", "cfus", "nfus", "rsfu", "wsfu", "csfu", "nsfu", "rsuf",
    "wsuf", "csuf", "nsuf", "rufs", "wufs", "cufs", "nufs", "rusf", "wusf",
    "cusf", "nusf"
]
