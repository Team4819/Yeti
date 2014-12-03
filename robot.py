import wpilib
import yeti
from examples import example_module_fail


context = yeti.Context()
context.start()
context.add_module(example_module_fail.Example())

class George(wpilib.IterativeRobot):

    def robotInit(self):
        context = yeti.Context()
        context.start()
        context.add_module(example_module_fail.Example())



#if __name__ == "__main__":
#    wpilib.run(George)
