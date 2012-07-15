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

    def __init__(self, name, email, password=None, uid=None):
        self._name = name
        self._email = email
        self._password = password

    def set_password(self, password):
        self._password = hash(password)

    def authenticate(self, password):
        return hash(password) == self._password

    def dictify(self):
        return {
            "password": self._password,
            "name": self._name,
            "email": self._email,
        }

    def get_key(self):
        return self._email


# ...somewhere you are working with real data...
from norm.context import Context
from norm.backends.dbm_backend import register # or riak, postgres, redis, etc.

context = Context()
register(context)
connection = context.get_connection("dbm:///tmp/database.db")
store = connection.get_store()
user = User(name="Joe", email="joe@email.com")
user.set_password("password")
store.save(user)
# ... later on ...
user = store.fetch("joe@email.com", User)
# or any implementation specific operations, like find(), increment(), etc.
```

The core idea is that a connection is separate from a storage layer is separate
from your actual business models. Not only does this free up any class in your
system to be persisted (as long as it implements the `dictify()` and `get_key()`
methods), but you can persist them in any compatible datastore. So if you are
saving objects to your "safe" SQL database, but also need to shove them down
a Redis PubSub channel, go for it.

Only the DBM backend is currently implemented. I'm going to go after a few that
I personally want to play with (Riak, Redis, maybe Postgres), but anyone can
implement their own Connection and Store in their own projects. Feedback at this
early stage would be LOVED.

The @norm.framework.* interfaces are obviously optional -- I like my tests telling
me when I forgot to implement a method, but others don't like their duck typing
constrained. :)
