from datetime import datetime

import pytest

from xivuniversalis.client import UniversalisClient


async def test_market_data(client: UniversalisClient):
    market_data = await client.get_market_data(4, "Crystal")

    assert market_data.item_id == 4
    assert market_data.hq is None
    assert market_data.nq

    assert market_data.nq.lowest_price.by_region
    assert market_data.nq.lowest_price.by_region > 0
    assert market_data.nq.lowest_price.by_dc
    assert market_data.nq.lowest_price.by_dc > 0
    assert market_data.nq.lowest_price.by_world is None
    assert market_data.nq.lowest_price.region_world_id
    assert market_data.nq.lowest_price.dc_world_id

    assert market_data.nq.average_price.by_region
    assert market_data.nq.average_price.by_region > 0
    assert market_data.nq.average_price.by_dc
    assert market_data.nq.average_price.by_dc > 0
    assert market_data.nq.average_price.by_world is None

    assert market_data.nq.last_sale.by_region
    assert market_data.nq.last_sale.by_region > 0
    assert market_data.nq.last_sale.region_world_id
    assert market_data.nq.last_sale.region_sold_at
    assert isinstance(market_data.nq.last_sale.region_sold_at, datetime)
    assert market_data.nq.last_sale.by_dc
    assert market_data.nq.last_sale.by_dc > 0
    assert market_data.nq.last_sale.dc_world_id
    assert market_data.nq.last_sale.dc_sold_at
    assert isinstance(market_data.nq.last_sale.dc_sold_at, datetime)
    assert market_data.nq.last_sale.by_world is None
    assert market_data.nq.last_sale.world_sold_at is None

    assert market_data.nq.sale_volume
    assert market_data.nq.sale_volume.by_region
    assert market_data.nq.sale_volume.by_region > 0
    assert market_data.nq.sale_volume.by_dc
    assert market_data.nq.sale_volume.by_dc > 0
    assert market_data.nq.sale_volume.by_world is None


async def test_multiple_market_data():
    client = UniversalisClient()
    market_data = await client.get_market_data([4, 7], "mateus")

    assert isinstance(market_data, dict)
    assert len(market_data) == 2
    assert market_data[4].item_id == 4
    assert market_data[7].item_id == 7


async def test_list_of_one_returns_dict(client: UniversalisClient):
    market_data = await client.get_market_data([4], "Crystal")

    assert isinstance(market_data, dict)
    assert len(market_data) == 1
    assert market_data[4].item_id == 4


