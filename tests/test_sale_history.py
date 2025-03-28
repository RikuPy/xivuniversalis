from datetime import datetime

import pytest

from xivuniversalis.client import UniversalisClient


@pytest.mark.asyncio
async def test_sale_history():
    client = UniversalisClient()
    sale_history = await client.get_sale_history(7, "Crystal", limit=25)

    for sale in sale_history:
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