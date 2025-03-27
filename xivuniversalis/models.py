from dataclasses import dataclass


@dataclass(kw_only=True)
class DataCenter:
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
    id: int
    name: str
    datacenter: DataCenter

    def __eq__(self, other):
        if isinstance(other, World):
            return self.id == other.id

        if isinstance(other, str):
            return self.name == other

        return False