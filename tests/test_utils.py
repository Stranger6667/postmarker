# coding: utf-8
import pytest

from postmarker.utils import chunks


@pytest.mark.parametrize('container, length, expected', (
    ([1, 2, 3, 4], 2, [[1, 2], [3, 4]]),
    ([], 500, []),
))
def test_chunks(container, length, expected):
    assert list(chunks(container, length)) == expected
