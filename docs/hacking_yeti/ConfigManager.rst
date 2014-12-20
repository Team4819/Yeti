
Config Manager
--------------

A Config Manager is the fourth layer of yeti. It provides the ability to use a configuration file to specify what module to load
at startup, and with what fallback modules.

Configuration files are built as follows:

::

    [StartupMods]
    drivetrain
    elevator
    modules.autonomous

    [drivetrain]
    modules.basic_drive
    modules.awesome_drive

    [elevator]
    modules.simple_elevator
    modules.pid_elevator


.. autoclass:: yeti.ConfigManager
    :members:
    :undoc-members:
    :show-inheritance:
