# coding: utf-8
from postmarker.models.bounces import Bounce


CASSETTE_NAME = 'bounces'


class TestModel:

    def test_get(self, bounce):
        assert isinstance(bounce, Bounce)

    def test_str(self, bounce):
        assert str(bounce) == 'Bounce: 734860869'

    def test_repr(self, bounce):
        assert repr(bounce) == '<Bounce: 734860869>'
