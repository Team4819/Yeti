import asyncio
import wpilib
import yeti
from yeti.wpilib_extensions import buttons

class DebugMod(yeti.Module):

    def module_init(self):
        self.joystick = wpilib.Joystick(0)
        reload_button = buttons.Button(self.joystick, 10)
        self.add_task(self.reload_mods(reload_button))

    @asyncio.coroutine
    def reload_mods(self, button):
        while True:
            yield from button.until_rising()
            print("Bark!")
            yield from asyncio.sleep(.02)