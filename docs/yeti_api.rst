
Yeti API
========

Yeti is designed to be a simplistic alternative to the command-based robot architecture.

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

Yeti also comes with a set of convenient extensions to wpilib, which are designed to make module programming easier.

.. autosummary::
    yeti.wpilib_extensions

.. toctree::
    :hidden:

    yeti_api/HookServer
    yeti_api/Module
    yeti_api/Context
    yeti_api/ModuleLoader
    yeti_api/ConfigManager
    yeti_api/Interfaces
    yeti_api/WpilibExtensions