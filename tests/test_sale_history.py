from datetime import datetime
from time import time

import pytest

from xivuniversalis.client import UniversalisClient


@pytest.mark.asyncio
async def test_sale_history():
    client = UniversalisClient()
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
