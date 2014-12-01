import wpilib
import yeti
import asyncio
from examples import example_module

asyncio.set_event_loop_policy(yeti.FPGATimedEventLoopPolicy())

class George(wpilib.IterativeRobot):

    def robotInit(self):
        module1 = example_module.Example()
        module1.start()
        wpilib.Timer.delay(5)
        yeti.trigger_event("tick")
        wpilib.Timer.delay(5)
        module1.stop()
        #module2 = Example()
        #module2.start()

if __name__ == "__main__":
    wpilib.run(George)
