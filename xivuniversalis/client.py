import urllib.parse
from datetime import datetime

import aiohttp

from xivuniversalis.errors import UniversalisServerError, UniversalisError
from xivuniversalis.models import DataCenter, World, Listing, SaleHistory, ListingResults


class UniversalisClient:
    def __init__(self):
        self.endpoint: str = "https://universalis.app/api/v2"

    async def get_listings(
        self,
        item_ids: int | list[int],
        world_dc_region: str,
        *,
        listing_limit: int | None = None,
        history_limit: int = 5,
        hq_only: bool = False,
    ) -> ListingResults:
        if isinstance(item_ids, int):
            item_ids = [item_ids]

        query_params = {"entries": history_limit}
        if listing_limit is not None:
            query_params["listings"] = listing_limit
        if hq_only:
            query_params["hq"] = 1
        query_params = urllib.parse.urlencode(query_params)

        listings_data = await self._request(
            f"{self.endpoint}/{world_dc_region}/{','.join(map(str, item_ids))}?{query_params}"
        )

        active = []
        sale_history = []
        for listing in listings_data["listings"]:
            active.append(
                Listing(
                    listing_id=int(listing["listingID"]),
                    updated_at=datetime.fromtimestamp(listing["lastReviewTime"]),
                    quantity=listing["quantity"],
                    price_per_unit=listing["pricePerUnit"],
                    total_price=listing["total"],
                    tax=listing["tax"],
                    world_name=listing["worldName"],
                    world_id=listing["worldID"],
                    hq=listing["hq"],
                    is_crafted=listing["isCrafted"],
                    on_mannequin=listing["onMannequin"],
                    retainer_id=int(listing["retainerID"]),
                    retainer_name=listing["retainerName"],
                    retainer_city=listing["retainerCity"],
                )
            )

        for sale in listings_data["recentHistory"]:
            sale_history.append(
                SaleHistory(
                    sold_at=datetime.fromtimestamp(sale["timestamp"]),
                    quantity=sale["quantity"],
                    price_per_unit=sale["pricePerUnit"],
                    total_price=sale["total"],
                    buyer_name=sale["buyerName"],
                    world_name=sale["worldName"],
                    world_id=sale["worldID"],
                )
            )

        return ListingResults(active=active, sale_history=sale_history)

    async def get_sale_history(self, item_id: int, world_dc_region: str, history_limit: int | None = None) -> list[SaleHistory]:
        query_params = {}
        if history_limit is not None:
            query_params["entriesToReturn"] = history_limit
        query_params = urllib.parse.urlencode(query_params)

        sale_data = await self._request(f"{self.endpoint}/history/{world_dc_region}/{item_id}?{query_params}")

        sale_history = []
        for sale in sale_data["entries"]:
            sale_history.append(
                SaleHistory(
                    sold_at=datetime.fromtimestamp(sale["timestamp"]),
                    quantity=sale["quantity"],
                    price_per_unit=sale["pricePerUnit"],
                    total_price=sale["pricePerUnit"] * sale["quantity"],
                    buyer_name=sale["buyerName"],
                    world_name=sale["worldName"],
                    world_id=sale["worldID"],
                )
            )

        return sale_history

    async def get_datacenters(self) -> list[DataCenter]:
        """
        Fetches a list of all datacenters and their worlds from Universalis.

        If you just need a list of worlds, the `worlds` method will be more efficient.

        Returns:
            list[DataCenter]: A list of DataCenter objects.

        Raises:
            UniversalisServerError: Universalis returned a server error or an invalid json response.
            UniversalisError: Universalis returned an unexpected error.
        """
        dc_resp = await self._request(f"{self.endpoint}/data-centers")
        world_resp = await self._request(f"{self.endpoint}/worlds")

        # We'll add in the datacenters later
        worlds = {}
        for _world in world_resp:
            # noinspection PyTypeChecker
            worlds[_world["id"]] = World(id=_world["id"], name=_world["name"], datacenter=None)

        # Build our DataCenter objects
        datacenters = []
        for _datacenter in dc_resp:
            dc_worlds = [worlds[world_id] for world_id in _datacenter["worlds"] if world_id in worlds]
            datacenters.append(DataCenter(name=_datacenter["name"], region=_datacenter["region"], worlds=dc_worlds))

        # Update worlds with their associated datacenters
        for _world in worlds.values():
            for _datacenter in datacenters:
                if _world in _datacenter.worlds:
                    _world.datacenter = _datacenter
                    break

        return datacenters

    async def get_worlds(self) -> list[World]:
        """
        Fetches a list of all worlds from Universalis.

        Returns:
            list[World]: A list of World objects.

        Raises:
            UniversalisServerError: Universalis returned a server error or an invalid json response.
            UniversalisError: Universalis returned an unexpected error.
        """
        world_resp = await self._request(f"{self.endpoint}/worlds")

        worlds = []
        for _world in world_resp:
            worlds.append(World(id=_world["id"], name=_world["name"]))

        return worlds

    async def _request(self, url: str) -> dict:
        async with aiohttp.request("GET", url) as response:
            try:
                match response.status:
                    case 200:
                        return await response.json()
                    case 500:
                        raise UniversalisServerError("Universalis returned a server error.")
                    case _:
                        raise UniversalisError(f"Universalis returned an unexpected {response.status} error.")
            except aiohttp.ContentTypeError:
                raise UniversalisServerError("Universalis returned an invalid json response.")
