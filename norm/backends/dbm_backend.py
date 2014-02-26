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
        return model.from_dict(json.loads(self._connection.fetch(key)))

    @norm.framework.serialize
    def save(self, instance):
        key = "%s:%s" % (instance.__class__.__name__, instance.identify())
        data = instance.to_dict()
        self._connection.save(key, json.dumps(data))
        self._connection.flush()


@norm.framework.connection
class DBMConnection(object):

    @classmethod
    def from_uri(cls, uri):
        path = uri.split("dbm://")[1]
        return cls(path)

    def __init__(self, path, flag="c"):
        self._path = path
        self._flag = flag

    def connect(self):
        self._dbm = dbm.open(self._path, self._flag)

    def disconnect(self):
        self._dbm.close()

    def get_store(self):
        return DBMStore(self)

    def flush(self):
        self._dbm.close()
        self.connect()

    def save(self, key, data):
        self._dbm[key] = data

    def fetch(self, key):
        return self._dbm[key]


def register(context):
    context.register_connection("dbm", DBMConnection)
