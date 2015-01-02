import wpilib
import yeti
from yeti import interfaces

class LittleRobot(wpilib.IterativeRobot):
    """
    This example demonstrates the capability of the full stack of yeti.
    """

    def robotInit(self):
        #First get the context initialized, as ModuleLoaders use it to run
        context = yeti.Context()
        context.start()

        #Then use a ConfigManager to load modules specified in a configuration file
        config_manager = yeti.ConfigManager()
        config_manager.parse_config("mods.conf")
        config_manager.load_startup_mods(context)

        #In this example we are using a datastream to communicate game mode between modules.
        self.mode_datastream = interfaces.get_datastream("gamemode", context=self.context)

    def teleopInit(self):
        self.mode_datastream.push_threadsafe({"mode": "teleop"}, context=self.context)

    def disabledInit(self):
        self.mode_datastream.push_threadsafe({"mode": "disabled"}, context=self.context)

    def autonomousInit(self):
        self.mode_datastream.push_threadsafe({"mode": "auto"}, context=self.context)

if __name__ == "__main__":
    wpilib.run(LittleRobot)
