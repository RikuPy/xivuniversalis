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
class Listing:
    listing_id: int
    updated_at: datetime
    quantity: int
    price_per_unit: int
    total_price: int
    tax: int
    world_id: int
    world_name: str
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
