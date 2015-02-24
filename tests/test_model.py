import mock
import unittest
from norm.model import Model, MissingIDField, UnknownField
from norm.field import Field, EmptyRequiredField


class TestModel(unittest.TestCase):

    def test_model(self):
        class M(Model):
            pass

        m = M()
        self.assertEqual({}, m.to_dict())

    def test_model_to_dict_defaults(self):
        class M(Model):
            field1 = Field(default="foobar")
            field2 = Field(default=None)
            field3 = Field()

        instance = M()
        self.assertEqual({
            "field1": "foobar",
            "field2": None
        }, instance.to_dict())

    def test_model_to_dict_construction(self):
        class M(Model):
            field = Field()

        instance = M(field="foobar")
        self.assertEqual({"field": "foobar"}, instance.to_dict())

    def test_model_construction_invalid_field(self):
        class M(Model):
            pass

        with self.assertRaises(UnknownField):
            M(field="foobar")

    def test_from_dict(self):
        class M(Model):
            field1 = Field(default="foobar")
            field2 = Field()

        model = M.from_dict({"field2": "thing"})
        self.assertEqual("foobar", model["field1"])
        self.assertEqual("foobar", model.field1)
        self.assertEqual("thing", model["field2"])
        self.assertEqual("thing", model.field2)

        model.field1 = "foo"
        self.assertEqual("foo", model["field1"])

    def test_identify(self):
        class M(Model):
            id = Field()

        model = M.from_dict({"id": "foobar"})
        self.assertEqual("foobar", model.identify())
        model.identify("a")
        self.assertEqual("a", model.id)

    def test_equals(self):
        class M(Model):
            id = Field()

        m1 = M.from_dict({"id": "foobar"})
        m2 = M.from_dict({"id": "foobar"})
        self.assertEqual(m1, m2)

    def test_raises_if_missing_id_field(self):
        class M(Model):
            pass

        m1 = M()
        with self.assertRaises(MissingIDField):
            m1.identify()

    def test_model_use(self):
        store = mock.Mock()
        store.fetch._NORM_DESERIALIZE = True

        class M(Model):
            pass

        MWrapped = M.use(store)
        MWrapped.store.fetch("foobar")

        store.fetch.assert_called_with(MWrapped, "foobar")

    def test_model_set_defaults(self):
        class M(Model):
            field = Field(default="whatever")

        m = M()
        self.assertEqual("whatever", m.field)

    def test_model_with_required(self):
        class M(Model):
            field = Field(required=True)

        with self.assertRaises(EmptyRequiredField):
            M()
