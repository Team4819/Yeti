import yeti
import asyncio
import wpilib
import math

class ArcadeDrive(yeti.Module):

    def module_init(self):
        self.joystick = wpilib.Joystick(0)
        self.front_left_motor = wpilib.Talon(1)
        self.back_left_motor = wpilib.Talon(2)
        self.front_right_motor = wpilib.Talon(3)
        self.back_right_motor = wpilib.Talon(4)
        self.drive = wpilib.RobotDrive(self.front_left_motor,
                                       self.back_left_motor,
                                       self.front_right_motor,
                                       self.back_right_motor)

        self.left_encoder = wpilib.Encoder(1, 2)
        self.right_encoder = wpilib.Encoder(3, 4)

        # Circumference in ft = 4in/12(in/ft)*PI
        self.left_encoder.setDistancePerPulse((4.0/12.0*math.pi) / 360.0)
        self.right_encoder.setDistancePerPulse((4.0/12.0*math.pi) / 360.0)

        self.rangefinder = wpilib.AnalogInput(6)
        self.gyro = wpilib.Gyro(1)

        wpilib.LiveWindow.addActuator("Drive Train", "Front_Left Motor", self.front_left_motor)
        wpilib.LiveWindow.addActuator("Drive Train", "Back Left Motor", self.back_left_motor)
        wpilib.LiveWindow.addActuator("Drive Train", "Front Right Motor", self.front_right_motor)
        wpilib.LiveWindow.addActuator("Drive Train", "Back Right Motor", self.back_right_motor)
        wpilib.LiveWindow.addSensor("Drive Train", "Left Encoder", self.left_encoder)
        wpilib.LiveWindow.addSensor("Drive Train", "Right Encoder", self.right_encoder)
        wpilib.LiveWindow.addSensor("Drive Train", "Rangefinder", self.rangefinder)
        wpilib.LiveWindow.addSensor("Drive Train", "Gyro", self.gyro)

        self.add_task(self.teleop_loop())

    @asyncio.coroutine
    def teleop_loop(self):
        while True:
            yield from yeti.get_event("teleoperated").wait()
            self.drive.arcadeDrive(-self.joystick.getY(), -self.joystick.getX())
            wpilib.SmartDashboard.putNumber("Left Distance", self.left_encoder.getDistance())
            wpilib.SmartDashboard.putNumber("Right Distance", self.right_encoder.getDistance())
            wpilib.SmartDashboard.putNumber("Left Speed", self.left_encoder.getRate())
            wpilib.SmartDashboard.putNumber("Right Speed", self.right_encoder.getRate())
            wpilib.SmartDashboard.putNumber("Gyro", self.gyro.getAngle())
            yield from asyncio.sleep(.05)