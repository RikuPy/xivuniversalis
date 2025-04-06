from xivuniversalis.client import UniversalisClient
import pytest


async def test_datacenters(client: UniversalisClient):
    datacenters = await client.get_datacenters()
    assert len(datacenters) > 0
    for datacenter in datacenters:
        assert datacenter.name
        assert datacenter.region
        assert datacenter.worlds
        assert len(datacenter.worlds) > 0
        for world_id, world in datacenter.worlds.items():
            assert world.id
            assert world.name
            assert world.datacenter == datacenter
            assert world in datacenter
