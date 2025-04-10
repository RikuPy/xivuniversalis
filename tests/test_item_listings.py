from datetime import datetime

from xivuniversalis.client import UniversalisClient


async def test_item_listings(client: UniversalisClient):
    listings = await client.get_listings(4, "Crystal", listing_limit=50, history_limit=5)
    assert listings.item_id == 4
    assert listings.last_updated
    assert isinstance(listings.last_updated, datetime)
    for listing in listings.active_listings:
        assert listing.updated_at
        assert isinstance(listing.updated_at, datetime)
        assert listing.is_hq is False
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

    assert len(listings.active_listings) <= 50

    for sale in listings.sale_history:
        assert sale.buyer_name
        assert sale.price_per_unit > 0
        assert sale.quantity > 0
        assert sale.sold_at
        assert isinstance(sale.sold_at, datetime)
        assert sale.total_price >= sale.price_per_unit
        assert isinstance(sale.is_hq, bool)
        assert isinstance(sale.on_mannequin, bool)
        assert sale.world_id
        assert isinstance(sale.world_id, int)
        assert sale.world_name

    assert len(listings.sale_history) <= 5


async def test_multiple_item_listings(client: UniversalisClient):
    listings = await client.get_listings([4, 7], "Crystal", listing_limit=10)
    assert len(listings) == 2
    assert listings[4].item_id == 4
    assert listings[7].item_id == 7


async def test_item_listings_using_world(client: UniversalisClient):
    listings = await client.get_listings(4, "Mateus")
    assert listings.item_id == 4
    assert listings.last_updated
    assert isinstance(listings.last_updated, datetime)
    for listing in listings.active_listings:
        assert listing.updated_at
        assert isinstance(listing.updated_at, datetime)
        assert listing.is_hq is False
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
        assert listing.world_id is None
        assert listing.world_name is None

    assert len(listings.active_listings) <= 50

    for sale in listings.sale_history:
        assert sale.buyer_name
        assert sale.price_per_unit > 0
        assert sale.quantity > 0
        assert sale.sold_at
        assert isinstance(sale.sold_at, datetime)
        assert sale.total_price >= sale.price_per_unit
        assert isinstance(sale.is_hq, bool)
        assert isinstance(sale.on_mannequin, bool)
        assert sale.world_id is None
        assert sale.world_name is None

    assert len(listings.sale_history) <= 5


async def test_list_of_one_returns_dict(client: UniversalisClient):
    listings = await client.get_listings([4], "Crystal")
    assert isinstance(listings, dict)
    assert len(listings) == 1
    assert listings[4].item_id == 4
