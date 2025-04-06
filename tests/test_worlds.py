from xivuniversalis.client import UniversalisClient
import pytest


async def test_worlds(client: UniversalisClient):
    worlds = await client.get_worlds()
    assert len(worlds) > 0
    for world_id, world in worlds.items():
        assert world.id
        assert world_id == world.id
        assert world.name