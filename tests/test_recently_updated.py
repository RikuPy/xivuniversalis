from datetime import datetime

from xivuniversalis.client import UniversalisClient
import pytest


async def test_recently_updated(client: UniversalisClient):
    listings = await client.get_recently_updated("Mateus")
    assert listings
    assert len(listings) > 0
    for listing in listings:
        assert listing.item_id
        assert listing.world_id
        assert listing.world_name
        assert listing.updated_at
        assert isinstance(listing.updated_at, datetime)
