from postmarker.models.message_streams import MessageStream


class TestModel:
    def test_get(self, message_stream):
        assert isinstance(message_stream, MessageStream)

    def test_repr(self, message_stream):
        assert repr(message_stream) == "<MessageStream: outbound>"

    def test_activate(self, message_stream):
        assert message_stream.activate() == "OK"


class TestManager:
    def test_all(self, postmark):
        message_streams = postmark.message_streams.all()
        assert len(message_streams) == 2
        assert all(isinstance(message_stream, MessageStream) for message_stream in message_streams)
