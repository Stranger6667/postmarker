import pytest

from postmarker.exceptions import ClientError

CASSETTE_NAME = "exceptions"


def test_raise(postmark):
    with pytest.raises(ClientError) as exc:
        postmark.templates.get(123)
    assert str(exc.value) == "[1101] The 'TemplateId' associated with this request is not valid or was not found."
    assert exc.value.error_code == 1101
