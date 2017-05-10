# coding: utf-8
from postmarker.core import PostmarkClient


def test_postmark_client():
    from postmarker.pytest import postmark

    mock = object()
    instance = next(postmark(mock))
    assert isinstance(instance, PostmarkClient)
    assert instance.mock is mock
