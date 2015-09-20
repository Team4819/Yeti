import wpilib
from robotpy_ext.misc import asyncio_policy
from os.path import join, abspath, dirname
from yeti import Engine


class YetiRobot(wpilib.IterativeRobot):
    """
    A standard robot class that starts a yeti engine.
    """

    config_dir = ""
    config_file = "yeti.yml"

    # Patch the asyncio policy to use wpilib.Timer.getFPGATime() rather than time.monotonic()
    asyncio_policy.patch_asyncio_policy()

    def robotInit(self):
        self.engine = Engine()
        self.engine.load_config(join(abspath(dirname(__file__)), "default.yml"))
        self.engine.load_config(join(self.config_dir, self.config_file))
        self.engine.spawn_thread()

    def teleopInit(self):
        self.engine.thread_coroutine(self.engine.run_tagged_methods("teleop"))

    def disabledInit(self):
        self.engine.thread_coroutine(self.engine.run_tagged_methods("disabled"))

    def autonomousInit(self):
        self.engine.thread_coroutine(self.engine.run_tagged_methods("autonomous"))
