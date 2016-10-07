# coding: utf-8
from postmarker.models.base import Model, ModelManager


class TestModel:

    def test_as_dict(self):
        instance = Model(value=1)
        assert instance.as_dict() == {'value': 1}

    def test_str(self):
        instance = Model(ID=1)
        assert str(instance) == 'Model: 1'


class TestModelManager:

    def test_str(self):
        assert str(ModelManager(None)) == 'ModelManager'

    def test_repr(self):
        assert repr(ModelManager(None)) == '<ModelManager>'
