import unittest
import norm.field


class Base(object):

    def __init__(self):
        self.data = {}

    @property
    def fields(self):
        return self.data


class TestField(unittest.TestCase):

    def test_field_descriptor(self):
        class Model(Base):
            field = norm.field.Field()

        m = Model()
        m.field = "foo"
        self.assertEqual("foo", m.field)
        self.assertEqual({"field": "foo"}, m.data)

    def test_default(self):
        class Model(Base):
            field = norm.field.Field(default="bar")

        m = Model()
        self.assertEqual("bar", m.field)

    def test_coerce(self):
        class Model(Base):
            field = norm.field.Field(coerce=str)

        m = Model()
        m.field = 5
        self.assertEqual("5", m.field)

    def test_serialize(self):
        class Model(Base):
            field = norm.field.Field(serialize=lambda x: "bar")

        m = Model()
        m.field = "foo"
        self.assertEqual("bar", m.field)

    def test_deserialize(self):
        class Model(Base):
            field = norm.field.Field(deserialize=lambda x: "bar")

        m = Model()
        m.field = "foo"
        self.assertEqual("bar", m.field)

    def test_typechecking(self):
        class Model(Base):
            field = norm.field.Field(unicode)

        m = Model()
        with self.assertRaises(TypeError):
            m.field = 5

        class Model(Base):
            field = norm.field.Field(unicode, coerce=unicode)

        # should coerce first...
        m = Model()
        m.field = 5
