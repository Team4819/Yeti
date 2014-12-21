import wpilib

import yeti
from yeti.module_interfaces import events


class GearsBot(wpilib.IterativeRobot):

    def robotInit(self):
        self.context = yeti.Context()
        self.config_manager = yeti.ConfigManager()
        self.config_manager.parse_config_file("mods.conf")
        self.config_manager.load_startup_mods(self.context)
        self.context.start()

    def teleopInit(self):
        events.trigger_event_threadsafe("teleoperated", context=self.context)
        print("Enabling!")
        events.trigger_event_threadsafe("enabled", context=self.context)

    def disabledInit(self):
        events.clear_event_threadsafe("teleoperated", context=self.context)
        events.clear_event_threadsafe("enabled", context=self.context)

if __name__ == "__main__":
    wpilib.run(GearsBot)
