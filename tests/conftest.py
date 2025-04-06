import pytest

from xivuniversalis import UniversalisClient


@pytest.fixture
async def client():
    return UniversalisClient()
