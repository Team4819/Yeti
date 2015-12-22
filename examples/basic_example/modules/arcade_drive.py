import wpilib
import yeti

class ArcadeDrive(yeti.Module):
    """
    A bare-bones example of an arcade drive module.
    """

    def module_init(self):
        # Setup a device references
        self.joystick = wpilib.Joystick(0)
        self.robot_drive = wpilib.RobotDrive(0, 1)

    def teleop_periodic(self):
        # Get the joystick values and drive the motors.
        self.arcade_drive(-self.joystick.getY(), -self.joystick.getX())

    def autonomous_init(self):
        self.robot_drive.setSafetyEnabled(False)

    def arcade_drive(self, y, x):
        self.robot_drive.arcadeDrive(y, x)

    def module_deinit(self):
        # Free the device reference
        self.robot_drive.free()
