
Module
------

The module is the first layer of yeti, and by far the most important. It provides a paper-thin layer for bundling and externally controlling asyncio coroutines.

The module class inherits from :py:class:`yeti.HookServer`, and the following hooks may be used to easily expand functionality in any way wished.

- module_init
- module_deinit
- add_task
- end_task
- exception

.. autoclass:: yeti.Module
    :members:
    :undoc-members:
    :show-inheritance:
