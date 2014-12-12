import wpilib
import yeti

class GearsBot(wpilib.IterativeRobot):

    def robotInit(self):
        self.context = yeti.Context()
        self.config_manager = yeti.ConfigManager()
        self.config_manager.parse_config_file("mods.conf")
        self.config_manager.load_startup_mods(self.context)
        self.context.start()

    def teleopInit(self):
        yeti.trigger_event_threadsafe("teleoperated", context=self.context)
        yeti.trigger_event_threadsafe("enabled", context=self.context)

    def disabledInit(self):
        yeti.reset_event_threadsafe("teleoperated", context=self.context)
        yeti.reset_event_threadsafe("enabled", context=self.context)

if __name__ == "__main__":
    wpilib.run(GearsBot)
