from datetime import datetime
from time import time

import pytest

from xivuniversalis.client import UniversalisClient


async def test_sale_history(client: UniversalisClient):
    now = time()
    sale_history = await client.get_sale_history(
        7,
        "Crystal",
        limit=25,
        min_sale_price=1,
        max_sale_price=999,
        entries_within=432000,
        entries_until=int(now - 86400)
    )

    for sale in sale_history:
        assert sale.item_id
        assert sale.item_id == 7
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

    assert len(sale_history) <= 25


async def test_multiple_sale_history(client: UniversalisClient):
    now = time()
    results = await client.get_sale_history(
        [4, 7],
        "Crystal",
        limit=25,
        min_sale_price=1,
        max_sale_price=999,
        entries_within=432000,
        entries_until=int(now - 86400)
    )

    for item_id, sale_history in results.items():
        assert item_id
        assert isinstance(item_id, int)
        assert isinstance(sale_history, list)
        for sale in sale_history:
            assert sale.item_id
            assert sale.item_id == item_id
            assert sale.buyer_name
            assert sale.price_per_unit > 0
            assert sale.quantity > 0
            assert sale.sold_at
            assert isinstance(sale.sold_at, datetime)
            assert sale.total_price >= sale.price_per_unit
            assert sale.world_id
            assert isinstance(sale.world_id, int)
            assert sale.world_name

        assert len(sale_history) <= 25


async def test_sale_history_using_world(client: UniversalisClient):
    results = await client.get_sale_history(7, "Mateus", limit=25)

    for sale_history in results:
        assert sale_history.item_id
        assert sale_history.item_id == 7
        assert sale_history.buyer_name
        assert sale_history.price_per_unit > 0
        assert sale_history.quantity > 0
        assert sale_history.sold_at
        assert isinstance(sale_history.sold_at, datetime)
        assert sale_history.total_price >= sale_history.price_per_unit
        assert isinstance(sale_history.is_hq, bool)
        assert isinstance(sale_history.on_mannequin, bool)
        assert sale_history.world_id is None
        assert sale_history.world_name is None


async def test_list_of_one_returns_dict(client: UniversalisClient):
    results = await client.get_sale_history([7], "Crystal", limit=25)

    assert isinstance(results, dict)
    assert len(results) == 1
    assert results[7][0].item_id == 7