
Using Yeti
==========


In robot.py
-----------

Here is a basic example on how to use yeti from robot.py

.. literalinclude:: ../examples/basic_example/robot.py

Yeti is extremely flexible, and can be used in whatever setup you wish. This example uses the full stack of yeti, which consists of the following components.

.. autosummary::
    yeti.Module
    yeti.Context
    yeti.ModuleLoader
    yeti.ConfigManager


Contexts are essentially containers for modules -- while modules can be used completely
independently, the rest of Yeti's components rely upon Contexts to mediate access to
loaded modules.

In this example, we start by initializing a Context, and running it's start() method. The
start() method causes the Context to spawn its thread and asyncio loop, returning immediately.::

   context = yeti.Context()
   context.start()

Once we have a running context, we need to load some modules. The :class:`ConfigManager` class
provides a convenient interface to load modules referenced in a config file. After initializing
the object, we tell it to parse the "mods.conf" config file. ::

       config_manager = yeti.ConfigManager()

       #Parse the config file "mods.conf"
       config_manager.parse_config("mods.conf")

       #Load modules listed under the "StartupMods" section
       config_manager.load_startup_mods(context)


Once we have some modules running, we need a way to let them know what mode the main robot loop is in. One
way of doing this is with the datastream interface, which is contained in the "interfaces" sub-package::

    def robotInit(self):
        #...lots of stuff...
        self.mode_datastream = interfaces.get_datastream("gamemode", context=self.context)

    def teleopInit(self):
        self.mode_datastream.push_threadsafe({"mode": "teleop"}, context=self.context)

    def disabledInit(self):
        self.mode_datastream.push_threadsafe({"mode": "disabled"}, context=self.context)

    def autonomousInit(self):
        self.mode_datastream.push_threadsafe({"mode": "auto"}, context=self.context)


Interfaces are documented in more depth here: :mod:`yeti.interfaces`

Modules
-------

TODO