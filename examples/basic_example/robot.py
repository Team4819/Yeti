import wpilib
import yeti
from yeti.interfaces import gamemode

class LittleRobot(wpilib.IterativeRobot):
    """
    This example demonstrates the capability of the full stack of yeti.
    """

    def robotInit(self):
        #First get the context initialized, as ModuleLoaders use it to run
        self.context = yeti.Context()
        self.context.start()

        #Then use a ConfigManager to load modules specified in a configuration file
        config_manager = yeti.ConfigManager()
        config_manager.parse_config("mods.conf")
        config_manager.load_startup_mods(self.context)

    def teleopInit(self):
        gamemode.set_gamemode(gamemode.TELEOPERATED, context=self.context)

    def disabledInit(self):
        gamemode.set_gamemode(gamemode.DISABLED, context=self.context)

    def autonomousInit(self):
        gamemode.set_gamemode(gamemode.AUTONOMOUS, context=self.context)

if __name__ == "__main__":
    wpilib.run(LittleRobot)
