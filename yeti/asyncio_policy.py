from asyncio.events import BaseDefaultEventLoopPolicy
from asyncio import SelectorEventLoop
from wpilib import Timer


class FPGATimedEventLoop(SelectorEventLoop):

    def time(self):
        return Timer.getFPGATimestamp()


class FPGATimedEventLoopPolicy(BaseDefaultEventLoopPolicy):
    _loop_factory = FPGATimedEventLoop


