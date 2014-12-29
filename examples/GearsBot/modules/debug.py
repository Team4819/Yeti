import asyncio
import wpilib
import yeti
from yeti.wpilib_extensions.buttons import Button

class Debug(yeti.Module):
    """
    A simple module for reloading all modules with the push of a button.
    """

    def module_init(self):
        self.joystick = wpilib.Joystick(0)
        self.add_task(self.reload_mods())

    @asyncio.coroutine
    def reload_mods(self):
        """Reload all mods when button 10 is pressed."""
        context = yeti.get_context()

        #Wait until the button is pressed.
        yield from Button(self.joystick, 10).until_rising()

        #Reload all modules with a loader object
        loaded_mods = context.get_modules()
        for module in loaded_mods:
            if hasattr(module, "loader"):
                module.loader.reload()