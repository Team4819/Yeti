
Engine
-------

    The Context class is the second layer of yeti, providing an interface to run modules in a group.

    Contexts are used by adding module objects to them, via :py:meth:`Context.load_module()`, and running :py:meth:`Context.start()`. The context will spawn a new thread and create an asyncio event loop for it.
    All loaded modules are then run within the new asyncio loop.

    Contexts also provide a system for inter-module interfaces to store data relevant to that module group. See :py:meth:`Context.get_interface_data()`

    .. autofunction:: yeti.set_context

    .. autofunction:: yeti.get_context

    .. autoclass:: yeti.Context
        :members:
        :show-inheritance: