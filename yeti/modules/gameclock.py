from yeti import Module


class GameClock(Module):
    """
    A built-in module for keeping track of current game mode.
    """

    _teleop = False
    _autonomous = False
    _disabled = False

    def module_init(self):
        pass

    def teleop_init(self):
        self._teleop = True
        self._autonomous = False
        self._disabled = False

    def autonomous_init(self):
        self._teleop = False
        self._autonomous = True
        self._disabled = False

    def disabled_init(self):
        self._teleop = False
        self._autonomous = False
        self._disabled = True

    def is_teleop(self):
        return self._teleop

    def is_autonomous(self):
        return self._autonomous

    def is_enabled(self):
        return not self._disabled

    def is_disabled(self):
        return self._disabled
