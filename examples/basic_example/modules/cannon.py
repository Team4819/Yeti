import yeti
import wpilib
import asyncio


class Cannon(yeti.Module):
    """
    A simple module to control a pneumatic cannon.
    """

    def module_init(self):
        self.fire_solenoid = wpilib.Solenoid(0)
        self.fire_joystick = wpilib.Joystick(0)
        self.triggers.on_rising_edge(self.fire_joystick.getTrigger, self.fire_cannon)

    async def fire_cannon(self, duration=.2):
        self.fire_solenoid.set(True)
        await asyncio.sleep(duration)
        self.fire_solenoid.set(False)

    def module_deinit(self):
        self.fire_solenoid.free()
