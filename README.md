nORM
====

nORM (which stands for No ORM) is a simple framework for separating your business
models from your database layer(s). Mostly, it grew from fat model frustration,
discussions about too much public data, etc. It's just a prototype
now, but the usage is supposed to be something like:

```python
import norm.framework

@norm.framework.model
class User(object):

    @classmethod
    def __new__(cls, name, email, password):
        password = cls._hash_password(password)
        return cls(name=name, email=email, password=password)

    @classmethod
    def _hash_password(cls, password):
        return hashlib.sha1(password).hexdigest

    def __init__(self, name, email, password):
        self._name = name
        self._email = email
        self._password = password

    def serialize(self):
        return {
            "password": self._password,
            "name": self._name,
            "email": self._email,
        }

    def identify(self):
        return self._email

    def authenticate(self, password):
        return password == self._hash_password(password)


# ...somewhere you are working with real data...
from norm.context import Context
from norm.backends.dbm_backend import register # or riak, postgres, redis, etc.

context = Context()
register(context)
connection = context.get_connection("dbm:///tmp/database.db")
store = connection.get_store()
store.register_model("user", User)
user = User.new(name="Joe", email="joe@email.com", password="foobar")
store.user.save(user)
user = store.user.fetch("joe@email.com")
user.authenticate("foobar")
```

The core idea is that a connection is separate from a storage layer is separate
from your actual business models. Not only does this free up any class in your
system to be persisted (as long as it implements the `serialize()` and `identify()`
methods), but you can persist them in any compatible datastore. So if you are
saving objects to your "safe" SQL database, but also need to shove them down
a Redis PubSub channel, go for it.

Only the DBM backend is currently implemented. I'm going to go after a few that
I personally want to play with (Riak, Redis, maybe Postgres), but anyone can
implement their own Connection and Store in their own projects. Feedback at this
early stage would be much appreciated.

The @norm.framework.* interfaces are obviously optional -- I like my tests telling
me when I forgot to implement a method, but others don't like their duck typing
constrained. :)
