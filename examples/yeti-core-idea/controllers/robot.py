import wpilib
import yeti



wpilib.run(yeti.YetiRobot)

class MyRobot(wpilib.IterativeRobot):

    def robotInit(self):
        left_motor = wpilib.Talon(1)
        right_motor = wpilib.Talon(2)

        self.left_controller = yeti.add_controller(left_motor, "left_cim_talon")
        self.right_controller = yeti.add_controller(right_motor, "right_cim_talon")

        self.drive_controller = yeti.get_controller("arcade_drive")

        self.joystick_1 = wpilib.Joystick(0)

        yeti.add_poll_stream("joystick", [int, int, int], 20)

    def teleopInit(self):
        self.drive_controller.bind("teleop")

    def teleopPeriodic(self):
        self.drive_controller.set(self.joystick_1.getX(),
                                  self.joystick_1.getY(),
                                  self.joystick_1.getZ())

    def disabledInit(self):
        self.drive_controller.free("teleop")