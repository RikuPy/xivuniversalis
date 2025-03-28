Overview
========

xivuniversalis is an unofficial asynchronous Python library for the `Universalis REST API <https://docs.universalis.app/>`__.

Important
=========
This library is still in development and is not guaranteed to be stable or feature-complete.

Installation
============
You can install this library using pip:

.. code:: shell

   pip install xivuniversalis

Usage
=====
A common use case for the Universalis API is looking up item listings. This can be done with the ``UniversalisClient.get_listings`` method,

.. code:: python

    import asyncio
    from xivuniversalis import UniversalisClient

    client = UniversalisClient()
    results = asyncio.run(client.get_listings(4, "crystal"))
    print(f"Found {len(results.active_listings)} listings")
    for listing in results.active_listings:
        print(f"[{listing.world_name}] {listing.quantity}x{listing.price_per_unit}/each ({listing.total_price} gil total)")

You must have the item ID's for the items you wish to look up.

If you need a source to obtain these from, you can use a service such as `xivapi <https://v2.xivapi.com/>`__.

You can also use the ``UniversalisClient.get_market_data`` method to find an item's cheapest listing, average price, and other useful metrics.

.. code:: python

    import asyncio
    from xivuniversalis import UniversalisClient

    client = UniversalisClient()
    market_data = asyncio.run(client.get_market_data(12056, "north-america"))
    print(f"[{market_data.nq.lowest_price.region_world_id}] Found listing for {market_data.nq.lowest_price.by_region} gil")
    print(f"Average listing price is {market_data.nq.average_price.by_region} gil")

You may have noticed above that we are referencing a world ID instead of a world name.

For endpoints where world names are not available, you can use the libraries ``UniversalisClient.get_worlds`` method to build a dictionary mapping that will allow you to easily convert world ID's back into human-readable world names.

.. code:: python

    import asyncio
    from xivuniversalis import UniversalisClient

    client = UniversalisClient()
    worlds = asyncio.run(client.get_worlds())
    world_id = 37
    print(worlds[world_id].name)

Links
=====
* `Documentation <https://xivuniversalis.readthedocs.io/en/latest/>`__
