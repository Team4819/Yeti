import wpilib
import yeti
from os.path import join

class George(wpilib.IterativeRobot):

    def robotInit(self):
        context = yeti.Context()
        context.start()
        config_manager = yeti.ConfigManager()
        config_manager.parse_config_file("mods.conf")
        config_manager.load_startup_mods(context)
        wpilib.Timer.delay(3)
        yeti.trigger_event_threadsafe("tick", context)
        #module_loader = yeti.ModuleLoader()
        #module_loader.set_context(context)
        #module_loader.load("examples.example_module_fail")



if __name__ == "__main__":
    wpilib.run(George)
