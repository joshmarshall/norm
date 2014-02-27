import unittest
import norm.field


class TestField(unittest.TestCase):

    def test_field_descriptor(self):
        class Model(dict):
            field = norm.field.Field()

        m = Model()
        m.field = "foo"
        self.assertEqual("foo", m.field)
        self.assertEqual({"field": "foo"}, m)

    def test_default(self):
        class Model(dict):
            field = norm.field.Field(default="bar")

        m = Model()
        self.assertEqual("bar", m.field)
        # should automatically set default value
        self.assertEqual("bar", m["field"])

    def test_default_callable(self):
        class Model(dict):
            field = norm.field.Field(default=lambda: "foo")

        m = Model()
        self.assertEqual("foo", m.field)
        self.assertEqual("foo", m["field"])

    def test_field_returns_none(self):
        class Model(dict):
            field = norm.field.Field()

        m = Model()
        self.assertEqual(None, m.field)
        self.assertFalse("field" in m)

    def test_coerce(self):
        class Model(dict):
            field = norm.field.Field(coerce=str)

        m = Model()
        m.field = 5
        self.assertEqual("5", m.field)

    def test_serialize(self):
        class Model(dict):
            field = norm.field.Field(serialize=lambda x: "bar")

        m = Model()
        m.field = "foo"
        self.assertEqual("bar", m.field)

    def test_deserialize(self):
        class Model(dict):
            field = norm.field.Field(deserialize=lambda x: "bar")

        m = Model()
        m.field = "foo"
        self.assertEqual("bar", m.field)

    def test_typechecking(self):
        class Model(dict):
            field = norm.field.Field(unicode)

        m = Model()
        with self.assertRaises(TypeError):
            m.field = 5

        class Model(dict):
            field = norm.field.Field(unicode, coerce=unicode)

        # should coerce first...
        m = Model()
        m.field = 5

    def test_get_field_name(self):
        field_instance = norm.field.Field()

        class Foo(object):
            field = field_instance

        self.assertEqual(
            "field", norm.field.get_field_name(Foo, field_instance))

    def test_get_field_name_no_matching_field(self):
        field_instance = norm.field.Field()

        class Foo(object):
            # doesn't include the field...
            pass

        with self.assertRaises(AttributeError):
            norm.field.get_field_name(Foo, field_instance)

    def test_get_all_field_names(self):
        class Foo(object):
            field1 = norm.field.Field()
            field2 = norm.field.Field()

        fields = norm.field.get_all_field_names(Foo)
        self.assertEqual(2, len(fields))
        self.assertTrue("field1" in fields)
        self.assertTrue("field2" in fields)

    def test_populate_defaults(self):
        class Foo(dict):
            field = norm.field.Field(default="foo")

        foo = Foo()
        norm.field.populate_defaults(foo)
        self.assertEqual("foo", foo.field)
        self.assertEqual("foo", foo["field"])

    def test_field_set_default_with_default(self):
        model = {}
        field = norm.field.Field(default="foo")
        result = field.set_default("field", model)
        self.assertEqual({"field": "foo"}, model)
        self.assertEqual("foo", result)

    def test_field_set_default_without_default(self):
        model = {}
        field = norm.field.Field()
        result = field.set_default("field", field)
        self.assertEqual({}, model)
        self.assertEqual(None, result)

    def test_deserialize_none_value(self):
        class Model(dict):
            field = norm.field.Field(deserialize=str)

        model = Model()
        self.assertEqual(None, model.field)

        # but falsy values should still be deserialized...
        model["field"] = 0
        self.assertEqual('0', model.field)

    def test_serialize_none_value(self):
        class Model(dict):
            field = norm.field.Field(serialize=str)

        model = Model()
        model.field = None
        self.assertEqual(None, model["field"])

        # but falsy values should still be serialized...
        model.field = 0
        self.assertEqual('0', model["field"])

    def test_full_example(self):

        # this functions much like the 'real' Model will when it gets
        # implemented, and thusly this test will likely be short lived.
        class Model(object):

            field1 = norm.field.Field(default="foobar")
            field2 = norm.field.Field()

            @classmethod
            def from_dict(cls, data):
                result = cls.__new__(cls)
                result._data = data
                norm.field.populate_defaults(result)
                return result

            def __getitem__(self, key):
                return self._data[key]

            def __setitem__(self, key, value):
                self._data[key] = value

        model = Model.from_dict({"field2": "thing"})
        self.assertEqual("foobar", model["field1"])
        self.assertEqual("foobar", model.field1)
        self.assertEqual("thing", model["field2"])
        self.assertEqual("thing", model.field2)

        model.field1 = "foo"
        self.assertEqual("foo", model["field1"])
