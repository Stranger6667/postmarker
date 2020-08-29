import pytest

from postmarker.utils import chunks, sizes


@pytest.mark.parametrize("container, length, expected", (([1, 2, 3, 4], 2, [[1, 2], [3, 4]]), ([], 500, [])))
def test_chunks(container, length, expected):
    assert list(chunks(container, length)) == expected


@pytest.mark.parametrize(
    "count, offset, size, expected",
    (
        (100, 0, 50, [(50, 0), (50, 50)]),
        (100, 10, 50, [(50, 10), (50, 60)]),
        (100, 10, 33, [(33, 10), (33, 43), (33, 76), (1, 109)]),
    ),
)
def test_sizes(count, offset, size, expected):
    assert list(sizes(count, offset, size)) == expected
