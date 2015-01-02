import asyncio

import wpilib

import yeti
from yeti import interfaces
from yeti.wpilib_extensions import Referee


class ArcadeDrive(yeti.Module):
    """
    This driver likes to play at the arcade!
    """

    def module_init(self):
        self.referee = Referee(self)
        self.joystick = wpilib.Joystick(0)

        self.left_motor = wpilib.Talon(1)
        self.referee.watch(self.left_motor)

        self.right_motor = wpilib.Talon(2)
        self.referee.watch(self.right_motor)

        self.drive = wpilib.RobotDrive(self.left_motor,self.right_motor)
        self.referee.watch(self.drive)

        self.gyro = wpilib.Gyro(1)
        self.referee.watch(self.gyro)

        wpilib.LiveWindow.addActuator("Drive Train", "Left Motor", self.left_motor)
        wpilib.LiveWindow.addActuator("Drive Train", "Right Motor", self.right_motor)
        wpilib.LiveWindow.addSensor("Drive Train", "Gyro", self.gyro)

        #Get the game-mode datastream
        self.gamemode_datastream = interfaces.get_datastream("gamemode")

        self.add_task(self.teleop_loop())

    @asyncio.coroutine
    def teleop_loop(self):
        #Grab the asyncio event to tell us when the robot is in teleoperated mode.
        teleop_event = self.gamemode_datastream.set_event(lambda d: d["mode"] == "teleop")
        while True:
            yield from teleop_event.wait()
            self.drive.arcadeDrive(-self.joystick.getY(), -self.joystick.getX())
            wpilib.SmartDashboard.putNumber("Left Distance", self.left_encoder.getDistance())
            wpilib.SmartDashboard.putNumber("Right Distance", self.right_encoder.getDistance())
            wpilib.SmartDashboard.putNumber("Left Speed", self.left_encoder.getRate())
            wpilib.SmartDashboard.putNumber("Right Speed", self.right_encoder.getRate())
            wpilib.SmartDashboard.putNumber("Gyro", self.gyro.getAngle())
            yield from asyncio.sleep(.05)
        self.gamemode_datastream.drop_event(teleop_event)