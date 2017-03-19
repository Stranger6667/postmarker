# coding: utf-8
import pytest

from postmarker.models.bounces import Bounce

from .._compat import patch


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
        assert bounce.dump is None

    def test_activate(self, bounce):
        assert bounce.activate() == 'OK'
        assert not bounce.Inactive


class TestManager:

    def test_tags(self, postmark):
        assert postmark.bounces.tags == []

    def test_deliverystats(self, postmark):
        assert postmark.bounces.deliverystats == {
            'Bounces': [
                {'Count': 141, 'Name': 'All'},
                {'Count': 136, 'Name': 'Hard bounce', 'Type': 'HardBounce'},
                {'Count': 4, 'Name': 'Soft bounce', 'Type': 'SoftBounce'},
                {'Count': 1, 'Name': 'Spam complaint', 'Type': 'SpamComplaint'}
            ],
            'InactiveMails': 136
        }

    def test_all(self, postmark):
        bounces = postmark.bounces.all(count=2)
        assert len(bounces) == 2
        assert all(isinstance(bounce, Bounce) for bounce in bounces)


class TestLoadAllBounces:

    @pytest.mark.parametrize('count, chunk_size, call_count', (
        (2, 50, 1),
        (2, 1, 2),
        (4, 1, 2),
        (None, 1, 2),
    ))
    def test_multiple_calls(self, postmark, count, chunk_size, call_count):
        with patch.object(postmark.bounces, 'max_chunk_size', chunk_size):
            with patch.object(postmark.bounces, 'call', wraps=postmark.bounces.call) as call:
                bounces = postmark.bounces.all(count=count)
                assert call.call_count == call_count
                assert len(bounces) == 2
                assert all(isinstance(bounce, Bounce) for bounce in bounces)
