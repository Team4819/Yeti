import yeti
import asyncio


class SimpleAuto(yeti.Module):
    """
    A simple drive-and-shoot autonomous mode.
    """

    def module_init(self):
        self.drivetrain = self.engine.get_module("drivetrain")
        self.cannon = self.engine.get_module("cannon")

    async def autonomous_init(self):
        # Drive forward
        self.drivetrain.arcade_drive(.2, 0)
        await asyncio.sleep(1)

        # Stop
        self.drivetrain.arcade_drive(0, 0)
        await asyncio.sleep(.2)

        # Fire cannon
        await self.cannon.fire_cannon()
