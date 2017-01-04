"""Simple DBM interface for norm."""

import dbm
import json
import norm.framework


@norm.framework.store
class DBMStore(object):

    def __init__(self, connection):
        self._connection = connection

    @norm.framework.deserialize
    def fetch(self, model, key):
        key = "%s:%s" % (model.__name__, key)
        result = self._connection.fetch(key)
        if result:
            result = model.from_dict(json.loads(result.decode("utf8")))
        return result

    @norm.framework.serialize
    def save(self, instance):
        key = "%s:%s" % (instance.__class__.__name__, instance.identify())
        data = instance.to_dict()
        self._connection.save(key, json.dumps(data).encode("utf8"))
        self._connection.flush()

    @norm.framework.deserialize
    def create(self, model, **kwargs):
        instance = model(**kwargs)
        self.save(instance)
        return instance

    @norm.framework.deserialize
    def find(self, model):
        prefix = "{}:".format(model.__name__)
        for key in self._connection._dbm.keys():
            key = key.decode("utf8")
            if key.startswith(prefix):
                identifier = key.split(prefix)[1]
                yield self.fetch(model, identifier)

    def delete(self, model, key):
        prefix = "{}:{}".format(model.__name__, key)
        self._connection.delete(prefix)


@norm.framework.connection
class DBMConnection(object):

    @classmethod
    def from_uri(cls, uri):
        path = uri.split("dbm://")[1]
        return cls(path)

    def __init__(self, path, flag="c"):
        self._path = path
        self._flag = flag
        self._open()

    def _open(self):
        self._dbm = dbm.open(self._path, self._flag)

    def disconnect(self):
        self._dbm.close()

    def get_store(self):
        return DBMStore(self)

    def flush(self):
        self._dbm.close()
        self._open()

    def save(self, key, data):
        self._dbm[key] = data

    def fetch(self, key):
        key = key.encode("utf8")
        if key not in self._dbm:
            return None
        return self._dbm[key]

    def delete(self, key):
        del self._dbm[key]


def register(context):
    context.register_connection("dbm", DBMConnection)
