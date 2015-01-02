
Hacking Yeti
============

One of the core design goals of yeti was to make it hackable in the extreme. Every component has tremendous freedom to be used and abused, with no complaint.

Yeti is constructed like an onion, each layer adding another set of features to the big picture, and can be easily modified or extended to suit your needs.

The primary components of yeti are layered as follows:

.. autosummary::
    yeti.Module
    yeti.Context
    yeti.ModuleLoader
    yeti.ConfigManager

Most components inherit from HookServer, which allows higher-level components to easily add functionality into classes beneath them.

.. autosummary::
    yeti.hook_server.HookServer

Inter-module communications are handled by Interfaces, which store data in Contexts via the :meth:`Context.get_interface_data()` method.
Two different Interfaces are default to yeti -- events and datastreams.

.. autosummary::
    yeti.interfaces

.. toctree::
    :hidden:

    hacking_yeti/HookServer
    hacking_yeti/Module
    hacking_yeti/Context
    hacking_yeti/ModuleLoader
    hacking_yeti/ConfigManager
    hacking_yeti/Interfaces