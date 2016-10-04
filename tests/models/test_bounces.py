# coding: utf-8
from postmarker.models.bounces import Bounce


CASSETTE_NAME = 'bounces'


class TestModel:

    def test_get(self, bounce):
        assert isinstance(bounce, Bounce)
        assert bounce.Inactive

    def test_str(self, bounce):
        assert str(bounce) == 'Bounce: 723626745'

    def test_repr(self, bounce):
        assert repr(bounce) == '<Bounce: 723626745>'

    def test_dump(self, bounce):
        assert bounce.dump == {}
