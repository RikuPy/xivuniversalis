from dataclasses import dataclass
from datetime import datetime


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
    worlds: list["World"]

    def __eq__(self, other):
        if isinstance(other, DataCenter):
            return (self.name, self.region) == (other.name, other.region)

        if isinstance(other, str):
            return self.name == other

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
            Only provided when worlds are retrieved via the `UniversalisClient.datacenters` method.
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
    item_id: int
    updated_at: datetime
    world_id: int
    world_name: str


@dataclass(kw_only=True, slots=True)
class Listing(ListingMeta):
    listing_id: int
    quantity: int
    price_per_unit: int
    total_price: int
    tax: int
    # creator_name: str  # todo: I don't believe either of these return values anymore, review to be sure
    # creator_id: int
    hq: bool
    is_crafted: bool
    # materia: list = field(default_factory=list)
    on_mannequin: bool
    retainer_id: int
    retainer_name: str
    retainer_city: int
    # seller_id: int  # todo: same as above, I don't believe this data is returned anymore


@dataclass(kw_only=True, slots=True)
class SaleHistory:
    sold_at: datetime
    quantity: int
    price_per_unit: int
    total_price: int
    buyer_name: str
    world_id: int
    world_name: str


@dataclass(kw_only=True, slots=True)
class ListingResults:
    item_id: int
    last_updated: datetime
    active: list[Listing]
    sale_history: list[SaleHistory]


@dataclass(kw_only=True, slots=True)
class LowestPrice:
    by_world: int | None
    by_dc: int | None
    dc_world_id: int | None
    by_region: int
    region_world_id: int


@dataclass(kw_only=True, slots=True)
class AverageSalePrice:
    by_world: float | None
    by_dc: float | None
    by_region: float


@dataclass(kw_only=True, slots=True)
class LastSale:
    world_price: int | None
    world_sold_at: datetime | None
    dc_price: int | None
    dc_sold_at: datetime | None
    dc_world_id: int | None
    region_price: int
    region_sold_at: datetime
    region_world_id: int


@dataclass(kw_only=True, slots=True)
class SaleVolume:
    by_world: float | None
    by_dc: float | None
    by_region: float


@dataclass(kw_only=True, slots=True)
class MarketData:
    lowest_price: LowestPrice
    average_price: AverageSalePrice
    last_sale: LastSale
    sale_volume: SaleVolume


@dataclass(kw_only=True, slots=True)
class MarketDataResults:
    item_id: int
    nq: MarketData
    hq: MarketData | None

