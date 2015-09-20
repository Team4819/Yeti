import asyncio
import wpilib
import yeti

class ArcadeDrive(yeti.Module):
    """
    A bare-bones example of an arcade drive module.
    """

    def module_init(self):

        # Get the gameclock module
        self.gameclock = self.engine.get_module("gameclock")

        # Setup a joystick
        self.joystick = wpilib.Joystick(0)

        # Setup the robotdrive
        self.robotdrive = wpilib.RobotDrive(0, 1)

    @asyncio.coroutine
    def teleop(self):
        while self.gameclock.is_teleop():
            # Get the joystick values and drive the motors.
            self.robotdrive.arcadeDrive(-self.joystick.getY(), -self.joystick.getX())

            # Wait for the rest of the code to run
            asyncio.sleep(.05)

    def module_deinit(self):
        # Free the robotdrive
        self.robotdrive.free()
