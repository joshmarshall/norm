import json
import mock
import unittest
from norm.field import Field, get_all_field_names, get_field_name
from norm.field import get_all_fields, populate_defaults, EMPTY
from norm.field import EmptyRequiredField
from norm.context import StoreContextWrapper

try:
    unicode
except NameError:
    unicode = str


class TestField(unittest.TestCase):

    def test_field_descriptor(self):
        class Model(dict):
            field = Field()

        m = Model()
        m.field = "foo"
        self.assertEqual("foo", m.field)
        self.assertEqual({"field": "foo"}, m)

    def test_default(self):
        class Model(dict):
            field = Field(default="bar")

        m = Model()
        self.assertEqual("bar", m.field)
        # should automatically set default value
        self.assertEqual("bar", m["field"])

    def test_default_callable(self):
        class Model(dict):
            field = Field(default=lambda: "foo")

        m = Model()
        self.assertEqual("foo", m.field)
        self.assertEqual("foo", m["field"])

    def test_coerce(self):
        class Model(dict):
            field = Field(coerce=str)

        m = Model()
        m.field = 5
        self.assertEqual("5", m.field)

    def test_serialize(self):
        class Model(dict):
            field = Field(serialize=lambda x, y: "bar")

        m = Model()
        m.field = "foo"
        self.assertEqual("bar", m.field)

    def test_deserialize(self):
        class Model(dict):
            field = Field(deserialize=lambda x, y: "bar")

        m = Model()
        m.field = "foo"
        self.assertEqual("bar", m.field)

    def test_typechecking(self):
        class Model(dict):
            field = Field(unicode)

        m = Model()
        with self.assertRaises(TypeError):
            m.field = 5

        class Model(dict):
            field = Field(unicode, coerce=unicode)

        # should coerce first...
        m = Model()
        m.field = 5

    def test_required_getter(self):
        class Model(dict):
            field = Field(required=True)

        m = Model()
        with self.assertRaises(EmptyRequiredField):
            getattr(m, "field")

    def test_get_field_name(self):
        field_instance = Field()

        class Foo(object):
            field = field_instance

        self.assertEqual(
            "field", get_field_name(Foo, field_instance))

    def test_get_field_name_no_matching_field(self):
        field_instance = Field()

        class Foo(object):
            # doesn't include the field...
            pass

        with self.assertRaises(AttributeError):
            get_field_name(Foo, field_instance)

    def test_get_all_fields(self):
        class Model(dict):
            field1 = Field(required=True)
            field2 = Field(default=None)

        for field_name, field in get_all_fields(Model):
            if field_name == "field1":
                self.assertEqual(True, field.required)
                self.assertEqual(EMPTY, field.default)
            else:
                self.assertEqual(None, field.default)
                self.assertEqual(False, field.required)

    def test_get_all_field_names(self):
        class Foo(object):
            field1 = Field()
            field2 = Field()

        fields = get_all_field_names(Foo)
        self.assertEqual(2, len(fields))
        self.assertTrue("field1" in fields)
        self.assertTrue("field2" in fields)

    def test_populate_defaults(self):
        class Foo(dict):
            field = Field(default="foo")

        foo = Foo()
        populate_defaults(foo)
        self.assertEqual("foo", foo.field)
        self.assertEqual("foo", foo["field"])

    def test_field_set_default_with_default(self):
        model = {}
        field = Field(default="foo")
        result = field.set_default("field", model)
        self.assertEqual({"field": "foo"}, model)
        self.assertEqual("foo", result)

    def test_field_set_default_without_default(self):
        model = {}
        field = Field()
        result = field.set_default("field", field)
        self.assertEqual({}, model)
        self.assertEqual(EMPTY, result)

    def test_deserialize_none_value(self):
        class Model(dict):
            field = Field(deserialize=lambda x, y: str(y), default=None)

        model = Model()
        self.assertEqual(None, model.field)

        # but falsy values should still be deserialized...
        model["field"] = 0
        self.assertEqual('0', model.field)

    def test_empty_field_access(self):

        class Model(dict):
            field = Field(default=EMPTY)

        instance = Model()
        self.assertEqual(None, instance.field)
        self.assertFalse("field" in instance)

    def test_serialize_none_value(self):
        class Model(dict):
            field = Field(serialize=lambda x, y: str(y), default=None)

        model = Model()
        populate_defaults(model)
        self.assertEqual(None, model["field"])
        self.assertEqual(None, model.field)

        # but falsy values should still be serialized...
        model.field = 0
        self.assertEqual('0', model["field"])

    def test_named_field(self):
        class Model(dict):
            field = Field(field_name="foo")

        model = Model()
        model.field = "foobar"
        self.assertEqual("foobar", model["foo"])

        model["foo"] = "other"
        self.assertEqual("other", model.field)

    def test_subclass_field(self):
        store = mock.Mock()
        store.save._NORM_SERIALIZE = True
        store.fetch._NORM_DESERIALIZE = False

        class Model(dict):
            use = StoreContextWrapper()
            field = Field()

        M = Model.use(store)

        model = M()
        model.field = "foobar"
        self.assertEqual("foobar", model["field"])

    def test_default_calls_serialize(self):
        class Model(dict):
            field = Field(
                list, serialize=lambda x, y: json.dumps(y),
                deserialize=lambda x, y: json.loads(y),
                default=lambda: [])

        instance = Model()
        self.assertEqual([], instance.field)
        self.assertEqual([], json.loads(instance["field"]))
