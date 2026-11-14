import pytest

from postmarker.models.server import Server

from ..conftest import aw, twin

pytestmark = [pytest.mark.vcr, pytest.mark.anyio]


async def get_server(client):
    return await aw(client.server.get())


async def test_edit(client):
    server = await get_server(client)
    assert not server.TrackOpens
    await aw(server.edit(TrackOpens=True))
    assert server.TrackOpens


async def test_str(client, flavor):
    server = await get_server(client)
    assert f"{server}" == f"{twin(Server, flavor).__name__}: example.com (1)"
