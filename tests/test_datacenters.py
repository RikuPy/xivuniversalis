from universalis.client import UniversalisClient
import pytest


@pytest.mark.asyncio
async def test_datacenters():
    client = UniversalisClient()
    datacenters = await client.datacenters()
    assert len(datacenters) > 0
    for datacenter in datacenters:
        assert datacenter.name
        assert datacenter.region
        assert datacenter.worlds
        assert len(datacenter.worlds) > 0
        for world in datacenter.worlds:
            assert world.id
            assert world.name
            assert world.datacenter == datacenter