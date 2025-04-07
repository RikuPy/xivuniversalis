from dataclasses import dataclass
from datetime import datetime

__all__ = [
    "DataCenter",
    "World",
    "ListingMeta",
    "Listing",
    "SaleHistory",
    "ListingResults",
    "LowestPrice",
    "AverageSalePrice",
    "LastSale",
    "SaleVolume",
    "MarketData",
    "MarketDataResults",
]


@dataclass(kw_only=True)
class DataCenter:
    """
    Represents an FFXIV datacenter.

    Attributes:
        name (str): The datacenter's name.
        region (str): The datacenter's region. (e.g. "North-America", "Japan", "Europe", ...)
        worlds (list['World']): A list of worlds in the datacenter.
    """

    name: str
    region: str
    worlds: dict[int, "World"]

    def __eq__(self, other):
        if isinstance(other, DataCenter):
            return (self.name, self.region) == (other.name, other.region)

        if isinstance(other, str):
            return self.name == other

        return False

    def __contains__(self, item):
        """
        Adds support for "World in Datacenter" operations.
        """
        if isinstance(item, World):
            return item.id in self.worlds

        if isinstance(item, int):
            return item in self.worlds

        return False

    def __str__(self):
        return self.name


@dataclass(kw_only=True)
class World:
    """
    Represents an FFXIV world.

    Attributes:
        id (int): The world's unique ID.
        name (str): The world's name.
        datacenter (DataCenter | None): The world's datacenter.
            Only provided when worlds are retrieved via the :meth:`~xivuniversalis.client.UniversalisClient.get_datacenters` method.
    """

    id: int
    name: str
    datacenter: DataCenter | None = None

    def __eq__(self, other):
        if isinstance(other, World):
            return self.id == other.id

        if isinstance(other, str):
            return self.name == other

        return False

    def __str__(self):
        return self.name


@dataclass(kw_only=True, slots=True)
class ListingMeta:
    """
    Represents basic metadata for a listing.

    Attributes:
        item_id (int): The item's unique ID.
        updated_at (datetime): The last time the listing was updated.
        world_id (int | None): The world's unique ID. None if a world is used for the server filter.
        world_name (str | None): The world's name. None if a world is used for the server filter.
    """
    item_id: int
    updated_at: datetime
    world_id: int | None
    world_name: str | None


@dataclass(kw_only=True, slots=True)
class Listing(ListingMeta):
    """
    Represents a market board listing for an item.

    Attributes:
        listing_id (int): The listing's unique ID.
        quantity (int): The quantity of items in this listing.
        price_per_unit (int): The price per item.
        total_price (int): The total price of the listing.
        tax (int): The tax on the listing.
        is_hq (bool): Whether the item is high quality.
        is_crafted (bool): Whether the item is crafted.
        on_mannequin (bool): Whether the item is on a mannequin.
        retainer_id (int): The retainer's unique ID.
        retainer_name (str): The retainer's name.
        retainer_city (int): The city where the retainer is located.
    """
    listing_id: int
    quantity: int
    price_per_unit: int
    total_price: int
    tax: int
    is_hq: bool
    is_crafted: bool
    # materia: list = field(default_factory=list) todo
    on_mannequin: bool
    retainer_id: int
    retainer_name: str
    retainer_city: int


@dataclass(kw_only=True, slots=True)
class SaleHistory:
    """
    Represents an item's sale history.

    Attributes:
        item_id (int): The item's unique ID.
        sold_at (datetime): The time the item was sold.
        quantity (int): The quantity of items sold.
        price_per_unit (int): The price per item.
        total_price (int): The total price of the sale.
        is_hq (bool): Whether the item was high quality.
        on_mannequin (bool): Whether the item was sold from a mannequin.
        buyer_name (str): The name of the buyer.
        world_id (int | None): The world's unique ID. None if a world is used for the server filter.
        world_name (str | None): The world's name. None if a world is used for the server filter.
    """
    item_id: int
    sold_at: datetime
    quantity: int
    price_per_unit: int
    total_price: int
    is_hq: bool
    on_mannequin: bool
    buyer_name: str
    world_id: int | None
    world_name: str | None


@dataclass(kw_only=True, slots=True)
class ListingResults:
    """
    Contains the results of a market board listing.

    Attributes:
        item_id (int): The item's unique ID.
        last_updated (datetime): The last time the listing was updated.
        active_listings (list[Listing]): A list of active listings for the item.
        sale_history (list[SaleHistory]): A list of past purchases for the item.
    """
    item_id: int
    last_updated: datetime
    active_listings: list[Listing]
    sale_history: list[SaleHistory]


@dataclass(kw_only=True, slots=True)
class LowestPrice:
    """
    Represents the lowest price for an item.

    Attributes:
        by_world (int | None): The lowest price for a specified world. Only available if a world filter was specified.
        by_dc (int | None): The lowest price for a specified datacenter. Only available if a world or datacenter filter was specified.
        dc_world_id (int | None): The ID of the world where the lowest listing price was found. Only available if a world or datacenter filter was specified.
        by_region (int | None): The lowest price for the entire region.
        region_world_id (int | None): The ID of the world where the lowest listing price in the region was found.
    """
    by_world: int | None
    by_dc: int | None
    dc_world_id: int | None
    by_region: int | None
    region_world_id: int | None


@dataclass(kw_only=True, slots=True)
class AverageSalePrice:
    """
    Represents the average sale price for an item.

    Attributes:
        by_world (float | None): The average sale price for a specified world. Only available if a world filter was specified.
        by_dc (float | None): The average sale price for a specified datacenter. Only available if a world or datacenter filter was specified.
        by_region (float | None): The average sale price for the entire region.
    """
    by_world: float | None
    by_dc: float | None
    by_region: float | None


@dataclass(kw_only=True, slots=True)
class LastSale:
    """
    Represents the most recently recorded sale of an item.

    Attributes:
        by_world (int | None): The price of the last sale in a specified world. Only available if a world filter was specified.
        world_sold_at (datetime | None): The date and time of the last sale in a specified world. Only available if a world filter was specified.
        by_dc (int | None): The price of the last sale in a specified datacenter. Only available if a world or datacenter filter was specified.
        dc_sold_at (datetime | None): The date and time of the last sale in a specified datacenter. Only available if a world or datacenter filter was specified.
        dc_world_id (int | None): The ID of the world where the last sale was made in a specified datacenter. Only available if a world or datacenter filter was specified.
        by_region (int | None): The price of the last sale in the region.
        region_sold_at (datetime | None): The date and time of the last sale in the region.
        region_world_id (int | None): The ID of the world where the last sale was made in the region.
    """
    by_world: int | None
    world_sold_at: datetime | None
    by_dc: int | None
    dc_sold_at: datetime | None
    dc_world_id: int | None
    by_region: int | None
    region_sold_at: datetime | None
    region_world_id: int | None


@dataclass(kw_only=True, slots=True)
class SaleVolume:
    """
    Represents the sale volume (velocity) of an item.

    Attributes:
        by_world (float | None): The sale volume for a specified world. Only available if a world filter was specified.
        by_dc (float | None): The sale volume for a specified datacenter. Only available if a world or datacenter filter was specified.
        by_region (float | None): The sale volume for the entire region.
    """
    by_world: float | None
    by_dc: float | None
    by_region: float | None


@dataclass(kw_only=True, slots=True)
class MarketData:
    """
    Contains market data for an item.

    Attributes:
        lowest_price (LowestPrice): The lowest price for the item.
        average_price (AverageSalePrice): The average sale price for the item.
        last_sale (LastSale): The most recent sale of the item.
        sale_volume (SaleVolume): The sale volume (velocity) of the item.
    """
    lowest_price: LowestPrice
    average_price: AverageSalePrice
    last_sale: LastSale
    sale_volume: SaleVolume


@dataclass(kw_only=True, slots=True)
class MarketDataResults:
    """
    Contains market data results for an item in both HQ and NQ variations.

    Attributes:
        item_id (int): The item's unique ID.
        nq (MarketData): The market data for the NQ variant of the item.
        hq (MarketData | None): The market data for the HQ variant of the item, or None if no HQ variant of the item exists.
    """
    item_id: int
    nq: MarketData
    hq: MarketData | None
