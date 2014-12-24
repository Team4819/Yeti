import asyncio
import wpilib
import yeti
from yeti.wpilib_extensions import buttons

class Debug(yeti.Module):
    """
    A simple module for reloading all modules with the push of a button.
    """

    def module_init(self):
        self.joystick = wpilib.Joystick(0)
        reload_button = buttons.Button(self.joystick, 10)
        self.add_task(self.reload_mods(reload_button))

    @asyncio.coroutine
    def reload_mods(self, button):
        context = yeti.get_context()
        while True:
            yield from button.until_rising()
            context.call_hook("reload")