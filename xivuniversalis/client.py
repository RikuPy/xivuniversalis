import urllib.parse
from datetime import datetime
from typing import overload

import aiohttp

from xivuniversalis.decorators import supports_multiple_ids
from xivuniversalis.errors import InvalidServerError, InvalidParametersError, UniversalisServerError
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
    ListingMeta,
)

__all__ = ["UniversalisClient"]


class UniversalisClient:
    """
    An asynchronous client for the Universalis REST API.

    Example:
        .. code:: python

            import asyncio
            from xivuniversalis import UniversalisClient

            client = UniversalisClient()
            results = asyncio.run(client.get_listings(4, "crystal"))
            print(f"Found {len(results.active_listings)} listings")
            for listing in results.active_listings:
                print(f"[{listing.world_name}] {listing.quantity}x{listing.price_per_unit}/each ({listing.total_price} gil total)")
    """

    def __init__(self):
        self.base_url: str = "https://universalis.app/api/v2"

    @overload
    async def get_listings(
        self,
        item_ids: int,
        server: str,
        *,
        listing_limit: int | None = None,
        history_limit: int | None = None,
        entries_within: int | None = None,
        hq_only: bool = False,
    ) -> ListingResults: ...

    @overload
    async def get_listings(
        self,
        item_ids: list[int],
        server: str,
        *,
        listing_limit: int | None = None,
        history_limit: int | None = None,
        entries_within: int | None = None,
        hq_only: bool = False,
    ) -> dict[int, ListingResults]: ...

    @supports_multiple_ids
    async def get_listings(
        self,
        item_ids: int | list[int],
        server: str,
        *,
        listing_limit: int | None = None,
        history_limit: int | None = None,
        entries_within: int | None = None,
        hq_only: bool = False,
    ) -> ListingResults | dict[int, ListingResults]:
        """
        Fetches the listings for a given item ID or list of items ID's.

        Args:
            item_ids (int | list[int]): The item ID or list of item IDs to fetch listings for.
            server (str): The world, datacenter, or region to filter the results by.
            listing_limit (int | None): The maximum number of listings to return. If not provided, Universalis will
                return all available listings.
            history_limit (int): The maximum number of sale history entries to return. If not provided, Universalis will
                default to 5 entries.
            entries_within (int | None): The amount of time before now to take entries within, in seconds.
            hq_only (bool): If True, only HQ items will be returned.

        Returns:
            ListingResults | dict[int, ListingResults]: A ListingResults object if a single item ID was provided.
                If a list of item ID's was provided, returns a dictionary containing item ID's as keys and
                ListingResults objects as values.

        Raises:
            InvalidServerError: The specified world, datacenter, or region does not exist.
            InvalidParametersError: An invalid parameter was passed to the API.
            UniversalisServerError: Universalis returned a server error or an invalid json response.
        """
        params = {}
        if history_limit:
            params["entries"] = history_limit
        if listing_limit is not None:
            params["listings"] = listing_limit
        if entries_within is not None:
            params["entriesWithin"] = entries_within
        if hq_only:
            params["hq"] = 1
        query_params = urllib.parse.urlencode(params)

        # If we have a single item ID, we need to wrap it in a list
        item_ids = item_ids if isinstance(item_ids, list) else [item_ids]
        resp = await self._request(f"{self.base_url}/{server}/{','.join(map(str, item_ids))}?{query_params}")

        # Iterate through the results
        items = resp["items"].values() if "items" in resp else [resp]
        results = {}
        for item in items:
            active = []
            sale_history = []
            for listing in item["listings"]:
                active.append(
                    Listing(
                        item_id=item["itemID"],
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
                        item_id=item["itemID"],
                        sold_at=datetime.fromtimestamp(sale["timestamp"]),
                        quantity=sale["quantity"],
                        price_per_unit=sale["pricePerUnit"],
                        total_price=sale["total"],
                        buyer_name=sale["buyerName"],
                        world_name=sale["worldName"],
                        world_id=sale["worldID"],
                    )
                )

            results[item["itemID"]] = ListingResults(
                item_id=item["itemID"],
                last_updated=datetime.fromtimestamp(item["lastUploadTime"] / 1000),
                active_listings=active,
                sale_history=sale_history,
            )

        return results

    @overload
    async def get_sale_history(
        self,
        item_ids: int,
        server: str,
        *,
        limit: int | None = None,
        min_sale_price: int | None = None,
        max_sale_price: int | None = None,
        entries_within: int | None = None,
        entries_until: int | None = None,
    ) -> list[SaleHistory]: ...

    @overload
    async def get_sale_history(
        self,
        item_ids: list[int],
        server: str,
        *,
        limit: int | None = None,
        min_sale_price: int | None = None,
        max_sale_price: int | None = None,
        entries_within: int | None = None,
        entries_until: int | None = None,
    ) -> dict[int, list[SaleHistory]]: ...

    @supports_multiple_ids
    async def get_sale_history(
        self,
        item_ids: int | list[int],
        server: str,
        *,
        limit: int | None = None,
        min_sale_price: int | None = None,
        max_sale_price: int | None = None,
        entries_within: int | None = None,
        entries_until: int | None = None,
    ) -> list[SaleHistory] | dict[int, list[SaleHistory]]:
        """
        Fetches the sale history for a given item ID or list of items ID's.

        Args:
            item_ids (int | list[int]): The item ID or list of item IDs to fetch sale history for.
            server (str): The world, datacenter, or region to filter the results by.
            limit (int | None): The maximum number of sale history entries to return. If not provided,
                Universalis will default to 1800 results.
            min_sale_price (int | None): The minimum sale price to filter the results by.
            max_sale_price (int | None): The maximum sale price to filter the results by.
            entries_within (int | None): The amount of time before entries_until or now to take entries within,
                in seconds. If not provided, Universalis will default to 7 days.
            entries_until (int | None): The UNIX timestamp in seconds to take entries until. If not provided,
                Universalis will default to now.

        Returns:
            list[SaleHistory] | dict[int, list[SaleHistory]]: A list of SaleHistory objects if a single item ID was provided.
                If a list of item ID’s was provided, returns a dictionary containing item ID's as keys and lists of
                SaleHistory objects as values.

        Raises:
            InvalidServerError: The specified world, datacenter, or region does not exist.
            InvalidParametersError: An invalid parameter was passed to the API.
            UniversalisServerError: Universalis returned a server error or an invalid json response.
        """
        params = {}
        if limit is not None:
            params["entriesToReturn"] = limit
        if min_sale_price is not None:
            params["minSalePrice"] = min_sale_price
        if max_sale_price is not None:
            params["maxSalePrice"] = max_sale_price
        if entries_within is not None:
            params["entriesWithin"] = entries_within
        if entries_until is not None:
            params["entriesUntil"] = entries_until
        query_params = urllib.parse.urlencode(params)

        # If we have a single item ID, we need to wrap it in a list
        item_ids = item_ids if isinstance(item_ids, list) else [item_ids]
        resp = await self._request(
            f"{self.base_url}/history/{server}/{','.join(map(str, item_ids))}?{query_params}"
        )

        items = resp["items"].values() if "items" in resp else [resp]
        results = {}
        for item in items:
            sale_history = []
            for sale in item["entries"]:
                sale_history.append(
                    SaleHistory(
                        item_id=item["itemID"],
                        sold_at=datetime.fromtimestamp(sale["timestamp"]),
                        quantity=sale["quantity"],
                        price_per_unit=sale["pricePerUnit"],
                        total_price=sale["pricePerUnit"] * sale["quantity"],
                        buyer_name=sale["buyerName"],
                        world_name=sale["worldName"],
                        world_id=sale["worldID"],
                    )
                )

            results[item["itemID"]] = sale_history

        return results

    @overload
    async def get_market_data(self, item_ids: int, server: str) -> MarketDataResults: ...

    @overload
    async def get_market_data(self, item_ids: list[int], server: str) -> dict[int, MarketDataResults]: ...

    @supports_multiple_ids
    async def get_market_data(
        self, item_ids: int | list[int], server: str
    ) -> MarketDataResults | dict[int, MarketDataResults]:
        """
        Fetches market data for a given item ID or list of items ID's.
        Returns data on the lowest price, average sale price, last sale, and sale volume.
        Results can be filtered by world, datacenter, or region. If filtered by world, you will also receive data
        for the datacenter and region. Similarly, if filtered by datacenter, you will receive data for the region as well.

        Args:
            item_ids (int | list[int]): The item ID or list of up to 100 item IDs to fetch market data for.
            server (str): The world, datacenter, or region to filter the results by.

        Returns:
            MarketDataResults | dict[int, MarketDataResults]: A MarketDataResults object if a single item ID was provided.
                If a list of item ID's was provided, returns a dictionary containing item ID's as keys and
                MarketDataResults objects as values.

        Raises:
            InvalidServerError: The specified world, datacenter, or region does not exist.
            InvalidParametersError: An invalid parameter was passed to the API.
            UniversalisServerError: Universalis returned a server error or an invalid json response.
        """
        # If we have a single item ID, we need to wrap it in a list
        item_ids = item_ids if isinstance(item_ids, list) else [item_ids]
        resp = await self._request(f"{self.base_url}/aggregated/{server}/{','.join(map(str, item_ids))}")

        # Iterate through the results
        results = {}
        for result in resp["results"]:
            market_data = {}
            # Iterate through both HQ and NQ results
            for type_ in ["hq", "nq"]:
                field = result[type_]["minListing"]
                # Items that cannot be HQ have no results
                if not field:
                    market_data[type_] = None
                    continue
                lowest_price = LowestPrice(
                    by_world=field["world"]["price"] if "world" in field else None,
                    by_dc=field["dc"]["price"] if "dc" in field else None,
                    dc_world_id=field["dc"]["worldId"] if "dc" in field else None,
                    by_region=field["region"]["price"],
                    region_world_id=field["region"]["worldId"],
                )

                field = result[type_]["averageSalePrice"]
                average_price = AverageSalePrice(
                    by_world=field["world"]["price"] if "world" in field else None,
                    by_dc=field["dc"]["price"] if "dc" in field else None,
                    by_region=field["region"]["price"],
                )

                field = result[type_]["recentPurchase"]
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

                field = result[type_]["dailySaleVelocity"]
                sale_count = SaleVolume(
                    by_world=field["world"]["quantity"] if "world" in field else None,
                    by_dc=field["dc"]["quantity"] if "dc" in field else None,
                    by_region=field["region"]["quantity"],
                )

                market_data[type_] = MarketData(
                    lowest_price=lowest_price,
                    average_price=average_price,
                    last_sale=last_sale,
                    sale_volume=sale_count,
                )

            results[result["itemId"]] = MarketDataResults(
                item_id=result["itemId"], hq=market_data["hq"], nq=market_data["nq"]
            )

        return results

    async def get_recently_updated(self, server: str, limit: int = None) -> list[ListingMeta]:
        """
        Fetches a list of recently updated items.

        Args:
            server (str): The world, datacenter, or region to filter the results by.
            limit (int | None): The maximum number of results to return. Supports a maximum of 200. If not provided,
                Universalis will default to 50.

        Returns:
            list[ListingMeta]: A list of ListingMeta objects containing basic listing metadata.

        Raises:
            InvalidServerError: The specified world, datacenter, or region does not exist.
            InvalidParametersError: An invalid parameter was passed to the API.
            UniversalisServerError: Universalis returned a server error or an invalid json response.
        """
        # Technically this endpoint has a split "world" and "dcName" parameter, but the API appears
        # to accept a world, dc, or even region in the world parameter without issue.
        params = {"world": server}
        if limit is not None:
            params["limit"] = limit
        query_params = urllib.parse.urlencode(params)
        resp = await self._request(f"{self.base_url}/extra/stats/most-recently-updated?{query_params}")
        results = []
        for item in resp["items"]:
            results.append(
                ListingMeta(
                    item_id=item["itemID"],
                    updated_at=datetime.fromtimestamp(item["lastUploadTime"] / 1000),
                    world_id=item["worldID"],
                    world_name=item["worldName"],
                )
            )

        return results

    async def get_tax_rates(self, world: str) -> dict[str, int]:
        """
        Fetches the tax rates for the specified world.

        Args:
            world (str): The name of the world to fetch tax rates for.

        Returns:
            dict[str, int]: A dictionary containing cities as keys and their associated tax rates as values.

        Raises:
            InvalidServerError: The specified world, datacenter, or region does not exist.
            UniversalisServerError: Universalis returned a server error or an invalid json response.
        """
        query_params = urllib.parse.urlencode({"world": world})
        return await self._request(f"{self.base_url}/tax-rates?{query_params}")

    async def get_datacenters(self) -> list[DataCenter]:
        """
        Fetches a list of all datacenters and their worlds from Universalis.

        If you just need a list of worlds, the :meth:`~xivuniversalis.client.UniversalisClient.get_worlds` method will be more efficient.

        Returns:
            list[DataCenter]: A list of DataCenter objects.

        Raises:
            UniversalisServerError: Universalis returned a server error or an invalid json response.
        """
        dc_resp = await self._request(f"{self.base_url}/data-centers")
        world_resp = await self._request(f"{self.base_url}/worlds")

        # We'll add in the datacenters later
        worlds = {}
        for _world in world_resp:
            # noinspection PyTypeChecker
            worlds[_world["id"]] = World(id=_world["id"], name=_world["name"], datacenter=None)

        # Build our DataCenter objects
        datacenters = []
        for _datacenter in dc_resp:
            dc_worlds = {world_id: worlds[world_id] for world_id in _datacenter["worlds"] if world_id in worlds}
            datacenters.append(DataCenter(name=_datacenter["name"], region=_datacenter["region"], worlds=dc_worlds))

        # Update worlds with their associated datacenters
        for _world in worlds.values():
            for _datacenter in datacenters:
                if _world.id in _datacenter.worlds:
                    _world.datacenter = _datacenter
                    break

        return datacenters

    async def get_worlds(self) -> dict[int, World]:
        """
        Fetches a dictionary of worlds from Universalis.

        Returns:
            dict[int, World]: A dictionary containing world IDs as keys and World objects as values.

        Raises:
            UniversalisServerError: Universalis returned a server error or an invalid json response.
        """
        world_resp = await self._request(f"{self.base_url}/worlds")

        worlds = {}
        for _world in world_resp:
            worlds[_world["id"]] = World(id=_world["id"], name=_world["name"])

        return worlds

    async def get_marketable_item_ids(self) -> list[int]:
        """
        Fetches a list of all marketable item IDs from Universalis.

        Returns:
            list[int]: A list of marketable item IDs.

        Raises:
            UniversalisServerError: Universalis returned a server error or an invalid json response.
        """
        return await self._request(f"{self.base_url}/marketable")

    async def _request(self, url: str) -> dict | list:
        async with aiohttp.request("GET", url) as response:
            try:
                match response.status:
                    case 200:
                        return await response.json()
                    case 400:
                        raise InvalidParametersError("An invalid parameter was passed to the API.")
                    case 404:
                        raise InvalidServerError("The specified world, datacenter, or region does not exist.")
                    case 500:
                        raise UniversalisServerError("Universalis returned an internal server error.")
                    case _:
                        raise UniversalisServerError(f"Universalis returned an unexpected {response.status} error.")
            except aiohttp.ContentTypeError:
                raise UniversalisServerError("Universalis returned an invalid json response.")
