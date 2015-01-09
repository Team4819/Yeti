Building a Robot Implementation
-------------------------------

While the standard Robot implementation that comes built-in to yeti can handle most situations,
advanced users are welcome to build their own. This document explains how to use yeti from your
own IterativeRobot implementation.

For an example, here is yeti's StandardRobot

.. literalinclude:: ../../yeti/robots/yeti_robot.py

Yeti is extremely flexible, and can be used in whatever setup you wish. This example uses the full
stack of yeti, which consists of the following components.

.. autosummary::
    yeti.Module
    yeti.Context
    yeti.ModuleLoader
    yeti.ConfigManager

Creating a Context
^^^^^^^^^^^^^^^^^^

Contexts are essentially containers for modules -- while modules can be used completely
independently, the rest of Yeti's components rely upon Contexts to mediate access to
loaded modules.

In this example, we start by initializing a Context, and running it's start() method. The
start() method causes the Context to spawn its thread and asyncio loop, returning immediately.
::

   context = yeti.Context()
   context.start()

Using a ConfigManager
^^^^^^^^^^^^^^^^^^^^^

Once we have a running context, we need to load some modules. The :class:`ConfigManager` class
provides a convenient interface to load modules referenced in a config file. After initializing
the object, we tell it to parse the "mods.conf" config file. ::

       config_manager = yeti.ConfigManager()

       #Parse the config file "mods.conf"
       config_manager.parse_config("mods.conf")

       #Load modules listed under the "StartupMods" section
       config_manager.load_startup_mods(context)

.. note:: You can read more about ConfigManager and its matching config files in the :class:`yeti.ConfigManager` documentation.

Gamemode Interface
^^^^^^^^^^^^^^^^^^

Once we have some modules running, we need a way to let them know what mode the main robot loop is in. One
way of doing this is with the gamemode interface, which is contained in the "interfaces" sub-package::

    def teleopInit(self):
        gamemode.set_gamemode(gamemode.TELEOPERATED, context=self.context)

    def disabledInit(self):
        gamemode.set_gamemode(gamemode.DISABLED, context=self.context)

    def autonomousInit(self):
        gamemode.set_gamemode(gamemode.AUTONOMOUS, context=self.context)

Here we use gamemode's :meth:`gamemode.set_gamemode()` method to set the game mode, providing it with the context to use.

.. note:: You can read more about Interfaces here:
          :class:`yeti.interfaces`.
