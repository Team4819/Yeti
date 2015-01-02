import wpilib
import yeti
from yeti.interfaces import gamemode

class GearsBot(wpilib.IterativeRobot):

    def robotInit(self):
        self.context = yeti.Context()
        self.config_manager = yeti.ConfigManager()
        self.config_manager.parse_config("mods.conf")
        self.config_manager.load_startup_mods(self.context)
        self.context.start()

    def teleopInit(self):
        print("teleop!")
        gamemode.set_gamemode(gamemode.TELEOPERATED, context=self.context)

    def disabledInit(self):
        gamemode.set_gamemode(gamemode.DISABLED, context=self.context)

    def autonomousInit(self):
        gamemode.set_gamemode(gamemode.AUTONOMOUS, context=self.context)


if __name__ == "__main__":
    wpilib.run(GearsBot)
