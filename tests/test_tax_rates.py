from xivuniversalis.client import UniversalisClient
import pytest


async def test_tax_rates(client: UniversalisClient):
    tax_rates = await client.get_tax_rates("Mateus")
    for city, tax_rate in tax_rates.items():
        assert city
        assert isinstance(city, str)
        assert tax_rate
        assert isinstance(tax_rate, int)
        assert tax_rate in [0, 3, 5]