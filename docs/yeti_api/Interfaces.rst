
Module Interfaces
=================

.. automodule:: yeti.interfaces

Interfaces are the primary method for inter-module communication. They store data in
the current :class:`yeti.Context` using it's :meth:`yeti.Context.get_interface_data()` method. Yeti comes
with a few default Interfaces, which should be sufficient for most uses. However, more may easily
be created to expand Yeti's functionality.

Events
------

interfaces.events is the first default interface mechanism. It provides a system for referencing
asyncio events by name.

.. automodule:: yeti.interfaces.events
    :members:
    :undoc-members:

Datastreams
-----------

interfaces.datastreams is another default interface mechanism. It provides a system for passing
around data, and triggering asyncio events upon certain conditions.

.. automodule:: yeti.interfaces.datastreams
    :members:
    :undoc-members:

Gamemode
--------

interfaces.gamemode is an interface mechanisim designed for communicating game mode between modules.

.. automodule:: yeti.interfaces.gamemode
    :members:
    :undoc-members: