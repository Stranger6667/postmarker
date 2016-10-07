# coding: utf-8


CASSETTE_NAME = 'server'


def test_edit(server):
    assert not server.TrackOpens
    server.edit(TrackOpens=True)
    assert server.TrackOpens


def test_str(server):
    assert ('%s' % server) == 'Server: example.com (1)'
