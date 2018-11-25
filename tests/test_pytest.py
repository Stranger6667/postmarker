# coding: utf-8
import sys

import pytest

from postmarker.core import PostmarkClient


def test_postmark_client(postmark_client, postmark_request):
    assert isinstance(postmark_client, PostmarkClient)
    assert postmark_client.mock is postmark_request


@pytest.mark.skipif(sys.version_info[0] == 3, reason="Mock is required only for Python 2")
def test_mock_not_installed():
    sys.modules["mock"] = None
    del sys.modules["postmarker._compat"]
    del sys.modules["postmarker.pytest"]

    from postmarker.pytest import postmark_request
    with pytest.raises(AssertionError, matches="To use pytest fixtures on Python 2.*"):
        list(postmark_request())
