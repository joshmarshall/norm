"""Test Norm interfaces."""

from unittest2 import TestCase
import norm.framework

class TestFramework(TestCase):

    def test_model_requires_dictify(self):
        with self.assertRaises(norm.framework.InvalidModel):
            @norm.framework.model
            class Model(object):
                def get_key(self):
                    pass

    def test_model_requires_get_key(self):
        with self.assertRaises(norm.framework.InvalidModel):
            @norm.framework.model
            class Model(object):
                def dictify(self):
                    pass

    def test_model_implementation(self):
        @norm.framework.model
        class Model(object):
            def get_key(self):
                pass
            def dictify(self):
                pass

    def test_store_implementation(self):
        @norm.framework.store
        class Store(object):
            def fetch(self, key, factory):
                pass
            def save(self, instance):
                pass
 
    def test_store_requires_fetch(self):
        with self.assertRaises(norm.framework.InvalidStore):
            @norm.framework.store
            class Store(object):
                def save(self, instance):
                    pass

    def test_store_requires_save(self):
        with self.assertRaises(norm.framework.InvalidStore):
            @norm.framework.store
            class Store(object):
                def fetch(self, key, factory):
                    pass

    def test_connection_implementation(self):
        @norm.framework.connection
        class Connection(object):
            def save(self, key, data):
                pass
            def fetch(self, key):
                pass
            def connect(self):
                pass
            @classmethod
            def from_uri(self, uri):
                pass

    def test_connection_requires_save(self):
        with self.assertRaises(norm.framework.InvalidConnection):
            @norm.framework.connection
            class Connection(object):
                def fetch(self, key):
                    pass
                def connect(self):
                    pass
                @classmethod
                def from_uri(self, uri):
                    pass

    def test_connection_requires_fetch(self):
        with self.assertRaises(norm.framework.InvalidConnection):
            @norm.framework.connection
            class Connection(object):
                def save(self, key, data):
                    pass
                def connect(self):
                    pass
                @classmethod
                def from_uri(self, uri):
                    pass

    def test_connection_requires_connect(self):
        with self.assertRaises(norm.framework.InvalidConnection):
            @norm.framework.connection
            class Connection(object):
                def save(self, key, data):
                    pass
                def fetch(self, key):
                    pass
                @classmethod
                def from_uri(self, uri):
                    pass

    def test_connection_requires_from_uri(self):
        with self.assertRaises(norm.framework.InvalidConnection):
            @norm.framework.connection
            class Connection(object):
                def save(self, key, data):
                    pass
                def fetch(self, key):
                    pass
                def connect(self):
                    pass
