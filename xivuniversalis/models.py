from dataclasses import dataclass


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
    worlds: list['World']

    def __eq__(self, other):
        if isinstance(other, DataCenter):
            return (self.name, self.region) == (other.name, other.region)

        if isinstance(other, str):
            return self.name == other

        return False


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