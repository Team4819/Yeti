import wpilib
import yeti


class George(wpilib.IterativeRobot):

    def robotInit(self):
        manager = yeti.ConfigManager()
        manager.parse_config_file("examples/mods.conf")
        manager.load_startup_mods()

        yeti.start_event("tick")
        wpilib.Timer.delay(10.0)
        yeti.stop_event("tick")
        #module2 = Example()
        #module2.start()

if __name__ == "__main__":
    wpilib.RobotBase.main(George)
