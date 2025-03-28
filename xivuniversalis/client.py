import urllib.parse
from datetime import datetime
from typing import overload

import aiohttp

from xivuniversalis.decorators import supports_multiple_ids
from xivuniversalis.errors import UniversalisServerError, UniversalisError
from xivuniversalis.models import (
    DataCenter,
    World,
    Listing,
    SaleHistory,
    ListingResults,
    MarketDataResults,
    LowestPrice,
    LastSale,
    AverageSalePrice,
    SaleVolume,
    MarketData,
)


class UniversalisClient:
    def __init__(self):
        self.endpoint: str = "https://universalis.app/api/v2"

    @overload
    async def get_listings(
        self,
        item_ids: int,
        world_dc_region: str,
        listing_limit: int | None = None,
        history_limit: int = 5,
        hq_only: bool = False,
    ) -> ListingResults: ...

    @overload
    async def get_listings(
        self,
        item_ids: list[int],
        world_dc_region: str,
        listing_limit: int | None = None,
        history_limit: int = 5,
        hq_only: bool = False,
    ) -> list[ListingResults]: ...

    @supports_multiple_ids
    async def get_listings(
        self,
        item_ids: int | list[int],
        world_dc_region: str,
        *,
        listing_limit: int | None = None,
        history_limit: int = 5,
        hq_only: bool = False,
    ) -> ListingResults | list[ListingResults]:
        query_params = {"entries": history_limit}
        if listing_limit is not None:
            query_params["listings"] = listing_limit
        if hq_only:
            query_params["hq"] = 1
        query_params = urllib.parse.urlencode(query_params)

        # If we have a single item ID, we need to wrap it in a list
        results = []
        item_ids = item_ids if isinstance(item_ids, list) else [item_ids]
        resp = await self._request(f"{self.endpoint}/{world_dc_region}/{','.join(map(str, item_ids))}?{query_params}")

        # Iterate through the results
        items = resp["items"].values() if "items" in resp else [resp]
        for item in items:
            active = []
            sale_history = []
            for listing in item["listings"]:
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

            for sale in item["recentHistory"]:
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

            results.append(
                ListingResults(
                    item_id=item["itemID"],
                    last_updated=datetime.fromtimestamp(item["lastUploadTime"] / 1000),
                    active=active,
                    sale_history=sale_history,
                )
            )

        return results

    async def get_sale_history(
        self,
        item_id: int,
        world_dc_region: str,
        *,
        history_limit: int | None = None,
        min_sale_price: int | None = None,
        max_sale_price: int | None = None,
    ) -> list[SaleHistory]:
        query_params = {}
        if history_limit is not None:
            query_params["entriesToReturn"] = history_limit
        if min_sale_price is not None:
            query_params["minSalePrice"] = min_sale_price
        if max_sale_price is not None:
            query_params["maxSalePrice"] = max_sale_price
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

    @overload
    async def get_market_data(self, item_ids: int, world_dc_region: str) -> MarketDataResults: ...

    @overload
    async def get_market_data(self, item_ids: list[int], world_dc_region: str) -> list[MarketDataResults]: ...

    @supports_multiple_ids
    async def get_market_data(
        self, item_ids: int | list[int], world_dc_region: str
    ) -> MarketDataResults | list[MarketDataResults]:
        """
        Fetches market data for a given item ID or list of items ID's.
        Returns data on the lowest price, average sale price, last sale, and sale volume.
        Results can be filtered by world, datacenter, or region. If filtered by world, you will also receive data
        for the datacenter and region. Similarly, if filtered by datacenter, you will receive data for the region as well.

        Args:
            item_ids (int | list[int]): The item ID or list of item IDs to fetch market data for.
            world_dc_region (str): The world, datacenter, or region to filter the results by.
        """
        # If we have a single item ID, we need to wrap it in a list
        results = []
        item_ids = item_ids if isinstance(item_ids, list) else [item_ids]
        resp = await self._request(f"{self.endpoint}/aggregated/{world_dc_region}/{','.join(map(str, item_ids))}")

        # Iterate through the results
        for _result in resp["results"]:
            market_data = {}
            # Iterate through both HQ and NQ results
            for _type in ["hq", "nq"]:
                field = _result[_type]["minListing"]
                # Items that cannot be HQ have no results
                if not field:
                    market_data[_type] = None
                    continue
                lowest_price = LowestPrice(
                    by_world=field["world"]["price"] if "world" in field else None,
                    by_dc=field["dc"]["price"] if "dc" in field else None,
                    dc_world_id=field["dc"]["worldId"] if "dc" in field else None,
                    by_region=field["region"]["price"],
                    region_world_id=field["region"]["worldId"],
                )

                field = _result[_type]["averageSalePrice"]
                average_price = AverageSalePrice(
                    by_world=field["world"]["price"] if "world" in field else None,
                    by_dc=field["dc"]["price"] if "dc" in field else None,
                    by_region=field["region"]["price"],
                )

                field = _result[_type]["recentPurchase"]
                last_sale = LastSale(
                    world_price=field["world"]["price"] if "world" in field else None,
                    world_sold_at=datetime.fromtimestamp(field["world"]["timestamp"] / 1000)
                    if "world" in field
                    else None,
                    dc_price=field["dc"]["price"] if "dc" in field else None,
                    dc_sold_at=datetime.fromtimestamp(field["dc"]["timestamp"] / 1000) if "dc" in field else None,
                    dc_world_id=field["dc"]["worldId"] if "dc" in field else None,
                    region_price=field["region"]["price"],
                    region_sold_at=datetime.fromtimestamp(field["region"]["timestamp"] / 1000),
                    region_world_id=field["region"]["worldId"],
                )

                field = _result[_type]["dailySaleVelocity"]
                sale_count = SaleVolume(
                    by_world=field["world"]["quantity"] if "world" in field else None,
                    by_dc=field["dc"]["quantity"] if "dc" in field else None,
                    by_region=field["region"]["quantity"],
                )

                market_data[_type] = MarketData(
                    lowest_price=lowest_price,
                    average_price=average_price,
                    last_sale=last_sale,
                    sale_volume=sale_count,
                )

            results.append(MarketDataResults(item_id=_result["itemId"], hq=market_data["hq"], nq=market_data["nq"]))

        return results

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
