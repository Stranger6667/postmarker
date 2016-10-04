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

    def test_activate(self, bounce):
        assert bounce.activate() == 'OK'
        assert not bounce.Inactive


class TestManager:

    def test_tags(self, server_client):
        assert server_client.bounces.tags == []

    def test_deliverystats(self, server_client):
        assert server_client.bounces.deliverystats == {
            'Bounces': [
                {'Count': 141, 'Name': 'All'},
                {'Count': 136, 'Name': 'Hard bounce', 'Type': 'HardBounce'},
                {'Count': 4, 'Name': 'Soft bounce', 'Type': 'SoftBounce'},
                {'Count': 1, 'Name': 'Spam complaint', 'Type': 'SpamComplaint'}
            ],
            'InactiveMails': 136
        }
