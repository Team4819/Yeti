import wpilib
import yeti
from examples.example_module import Example

class George(wpilib.IterativeRobot):

    def robotInit(self):
        module1 = Example()
        module1.start()

if __name__ == "__main__":
    wpilib.RobotBase.main(George)
