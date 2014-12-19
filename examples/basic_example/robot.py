import wpilib
import yeti


class LittleRobot(wpilib.IterativeRobot):

    def robotInit(self):
        context = yeti.Context()
        context.start()
        config_manager = yeti.ConfigManager()
        config_manager.parse_config_file("mods.conf")
        config_manager.load_startup_mods(context)


if __name__ == "__main__":
    wpilib.run(LittleRobot)
