import wpilib
import yeti


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
        config_manager.parse_config_file("mods.conf")
        config_manager.load_startup_mods(context)


if __name__ == "__main__":
    wpilib.run(LittleRobot)
