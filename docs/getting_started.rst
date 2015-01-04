
Getting Started
===============

What is yeti?
-------------

Yeti is a Python runtime framework designed for use on FIRST Robotics Competition Robots.
Yeti effectively isolates the robot-specific python code of your robot into "Modules" --
independent python files dynamically loaded at run-time. Modules can be freely loaded,
unloaded, replaced, and modified at any time. This allows you to easily build structured
robot programs, with mechanisms to promote rapid development and in-game failure recovery.

.. note:: This guide assumes some familiarity with RobotPy and python in general.

          If this is the first you have heard of RobotPy, you can read about it here:
          `About RobotPy <http://robotpy.github.io/about/>`_

.. note:: Yeti heavily utilizes asyncio, which is an asynchronous library that comes default
          with python. Some knowledge of asyncio would definitely be helpful, but not entirely
          necessary for this guide.

          You can read more about asyncio here: `Asyncio Documentation <https://docs.python.org/3.4/library/asyncio.html>`_

Installing Yeti
---------------

Yeti can be installed with pip, or with the robotpy installer.

With the robotpy installer
::

   #Connected to internet
   python3 installer.py download yeti

   #Connected to RoboRIO
   python3 installer.py install yeti

Or with pip
::

   pip install yeti

Using Yeti
----------

Here is a basic example on how to use yeti from robot.py

.. literalinclude:: ../examples/basic_example/robot.py

Yeti is extremely flexible, and can be used in whatever setup you wish. This example uses the full stack of yeti, which consists of the following components.

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

.. note:: You can read more about Interfaces here: :mod:`yeti.interfaces`.

Building Modules
----------------

A Basic Example
^^^^^^^^^^^^^^^

Here is a basic example for a drivetrain module. It contains all of the code required for reading values from joysticks, and driving a two-motor chassis.

.. literalinclude:: ../examples/basic_example/modules/arcade_drive.py

.. note:: Here is where asyncio comes to play. You will nearly always want to import asyncio when creating
          Modules, you will see why later on.

The Module Object
^^^^^^^^^^^^^^^^^
The module itself is a class inheriting from the base module type: :class:`yeti.module`.

module_init
^^^^^^^^^^^
This is called upon module startup. Here is where you should initialize all of your wpilib refrences, get
interfaces squared away, and just get everything woken up.

::

     def module_init(self):
        #Initialize the Referee for the module.
        self.referee = Referee(self)

        #Setup a joystick
        self.joystick = wpilib.Joystick(0)
        self.referee.watch(self.joystick)

        #Setup the robotdrive
        self.robotdrive = wpilib.RobotDrive(0, 1)
        self.referee.watch(self.robotdrive)

.. note:: Notice the :class:`Referee` object we initialize here. The referee is a little utility class who's job is to
          ensure that wpilib objects get cleanly deallocated should your module get unloaded. Make it a habit to have
          a referee :meth:`Referee.watch()` any wpilib objects you have created.

coroutines
^^^^^^^^^^
.. note:: In breif, asyncio coroutines are fake threads. They have their own train of execution, deferring control
          whenever they "yeild from" something. To initialize a coroutine, use the "@asyncio.coroutine" decorator,
          as seen below. For more information, read the "Asyncio Documentation"

Here is the run loop used in the above module example:

::

    @asyncio.coroutine
    def teleop_loop(self):

        #Loop forever
        while True:
            #Wait until we are in teleop mode.
            yield from gamemode.wait_for_teleop()

            #Get the joystick values and drive the motors.
            self.robotdrive.arcadeDrive(-self.joystick.getY(), -self.joystick.getX())

            #Pause for a moment to let the rest of the code run.
            yield from asyncio.sleep(.05)

Since this is a coroutine, and we don't have any reason for it to stop without the module
getting unloaded, we use an infinite loop. For each iteration we wait for the robot to
be in teleoperated mode before setting the RobotDrive values. Before we loop back, we
sleep for .05 of a second to let the rest of the robot program run.

.. note:: "yield from" is used to transition from one coroutine's execution to another.
          "gamemode.wait_for_teleop()" Is a coroutine, supplied by the gamemode interface,
          which will pause execution in this "fake thread" until the robot is put into
          teleoperated mode. When this finishes, execution will return to our coroutine.

.. note:: Rather than using python's native time.sleep(), or wpilib's Timer.delay(), always
          use asyncio.sleep(), which allows other coroutines to execute.

Yeti WebUI
----------
Yeti comes preinstalled with a convenient WebUI, where you can control what is
going on with loaded modules. From here you can load, unload, and reload any module
with the click of a button.

To run the webui, set "yeti.preloaded_modules.webui" to load from your module
config file. The http server will start up on port 8080, and you should be able
to reach it at <computer_ip>:8080/index.html .

.. image:: images/WebUI.png