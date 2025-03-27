from datetime import datetime

import pytest

from xivuniversalis.client import UniversalisClient


@pytest.mark.asyncio
async def test_item_listings():
    client = UniversalisClient()
    listings = await client.get_listings(7, "Crystal", listing_limit=50, history_limit=5)
    for listing in listings.active:
        assert listing.updated_at
        assert isinstance(listing.updated_at, datetime)
        assert listing.hq is False
        assert listing.is_crafted is False
        assert listing.listing_id
        assert isinstance(listing.listing_id, int)
        assert listing.price_per_unit > 0
        assert listing.quantity > 0
        assert listing.retainer_city
        assert listing.retainer_id
        assert isinstance(listing.retainer_id, int)
        assert listing.retainer_name
        assert listing.tax > 0
        assert listing.total_price >= listing.price_per_unit
        assert listing.world_id
        assert isinstance(listing.world_id, int)
        assert listing.world_name

    assert len(listings.active) <= 50

    for sale in listings.sale_history:
        assert sale.buyer_name
        assert sale.price_per_unit > 0
        assert sale.quantity > 0
        assert sale.sold_at
        assert isinstance(sale.sold_at, datetime)
        assert sale.total_price >= sale.price_per_unit
        assert sale.world_id
        assert isinstance(sale.world_id, int)
        assert sale.world_name

    assert len(listings.sale_history) <= 5