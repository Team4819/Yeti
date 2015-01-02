import wpilib
import yeti
from yeti import interfaces


class GearsBot(wpilib.IterativeRobot):

    def robotInit(self):
        self.context = yeti.Context()
        self.config_manager = yeti.ConfigManager()
        self.config_manager.parse_config("mods.conf")
        self.config_manager.load_startup_mods(self.context)
        self.context.start()
        self.mode_datastream = yeti.interfaces.get_datastream("gamemode", context=self.context)

    def teleopInit(self):
        self.mode_datastream.push_threadsafe({"mode": "teleop", "enabled": True}, context=self.context)

    def disabledInit(self):
        self.mode_datastream.push_threadsafe({"mode": "disabled", "enabled": False}, context=self.context)

    def autonomousInit(self):
        self.mode_datastream.push_threadsafe({"mode": "auto", "enabled": True}, context=self.context)

if __name__ == "__main__":
    wpilib.run(GearsBot)
