from postmarker.core import PostmarkClient


def test_postmark_client(postmark_client, postmark_request):
    assert isinstance(postmark_client, PostmarkClient)
    assert postmark_client.mock is postmark_request
