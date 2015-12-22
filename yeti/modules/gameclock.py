from yeti import Module
import asyncio

class GameClock(Module):
    """
    A built-in module for keeping track of current game mode.
    """

    _teleop = False
    _autonomous = False
    _disabled = False

    def module_init(self):
        pass

    def teleop(self):
        self._teleop = True
        self._autonomous = False
        self._disabled = False

    def autonomous(self):
        self._teleop = False
        self._autonomous = True
        self._disabled = False

    def disabled(self):
        self._teleop = False
        self._autonomous = False
        self._disabled = True

    def is_teleop(self):
        return self.teleop

    def is_autonomous(self):
        return self.autonomous

    def is_enabled(self):
        return not self.disabled

    def is_disabled(self):
        return self.disabled
