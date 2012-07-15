"""Simple DBM interface for norm."""

import dbm
import json
import norm.framework

@norm.framework.store
class DBMStore(object):

    def __init__(self, connection):
        self._connection = connection

    def fetch(self, key, factory):
        key = "%s:%s" % (factory.__name__, key)
        return factory(**json.loads(self._connection.fetch(key)))

    def save(self, instance):
        key = "%s:%s" % (instance.__class__.__name__, instance.get_key())
        data = instance.dictify()
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

    def save(self, key, data):
        self._dbm[key] = data

    def fetch(self, key):
        return self._dbm[key]

    def flush(self):
        self._dbm.close()
        self.connect()


def register(context):
    context.register_connection("dbm", DBMConnection)
    context.register_store("dbm", DBMStore)
