from xivuniversalis.client import UniversalisClient
import pytest


async def test_marketable(client: UniversalisClient):
    marketable_items = await client.get_marketable_item_ids()
    assert marketable_items
    assert isinstance(marketable_items, list)
    assert isinstance(marketable_items[0], int)
