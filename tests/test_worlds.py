from xivuniversalis.client import UniversalisClient
import pytest


@pytest.mark.asyncio
async def test_worlds():
    client = UniversalisClient()
    worlds = await client.get_worlds()
    assert len(worlds) > 0
    for world in worlds:
        assert world.id
        assert world.name