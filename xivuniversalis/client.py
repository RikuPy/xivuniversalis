import aiohttp

from xivuniversalis.errors import UniversalisServerError, UniversalisError
from xivuniversalis.models import DataCenter, World


class UniversalisClient:
    def __init__(self):
        self.endpoint: str = "https://universalis.app/api/v2"

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
