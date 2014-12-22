import asyncio

import wpilib

import yeti
from yeti.wpilib_extensions import referee

class Claw(yeti.Module):

    control_data_default = {"claw_open": False, "elevator_pos": 0, "wrist_pos": 0}
    state_data = {"claw_open": False, "elevator_pos": 0, "wrist_pos": 0}

    def module_init(self):
        self.referee = referee.Referee(self)

        self.joystick = wpilib.Joystick(0)

        self.claw_motor = wpilib.Victor(7)
        self.referee.watch(self.claw_motor)

        self.claw_contact = wpilib.DigitalInput(5)
        self.referee.watch(self.claw_contact)

        #Get the control datastream
        self.control_datastream = yeti.get_datastream("claw_control")

        #Get the state datastream
        self.state_datastream = yeti.get_datastream("claw_state")
        self.state_datastream.set(self.state_data)

        self.elevator_motor = wpilib.Victor(5)
        self.referee.watch(self.elevator_motor)
        self.elevator_pot = wpilib.AnalogPotentiometer(2)    # defaults to meters
        self.referee.watch(self.elevator_pot)

        self.wrist_motor = wpilib.Victor(6)
        self.referee.watch(self.wrist_motor)
        self.wrist_pot = wpilib.AnalogPotentiometer(3)
        self.referee.watch(self.wrist_pot)

        #Get the PID controller
        self.elevator_controller = wpilib.PIDController(18, 0.2, 0, self.get_pid_in, self.set_pid_out)
        self.elevator_controller.enable()
        self.referee.watch(self.elevator_controller)

        self.wrist_controller = wpilib.PIDController(0.05, 0, 0, self.get_pid_in, self.set_pid_out)
        self.wrist_controller.enable()
        self.referee.watch(self.wrist_controller)

        # Let's show everything on the LiveWindow
        wpilib.LiveWindow.addActuator(self.name, "Claw Motor", self.claw_motor)
        wpilib.LiveWindow.addActuator(self.name, "Claw Limit Switch", self.claw_contact)


        # Let's show everything on the LiveWindow
        wpilib.LiveWindow.addActuator(self.name, "Elevator Motor", self.elevator_motor)
        wpilib.LiveWindow.addSensor(self.name, "Elevator Pot", self.elevator_pot)
        wpilib.LiveWindow.addActuator(self.name, "Elevator PID", self.elevator_controller)

        # Let's show everything on the LiveWindow
        wpilib.LiveWindow.addActuator(self.name, "Wrist Motor", self.wrist_motor)
        wpilib.LiveWindow.addSensor(self.name, "Wrist Pot", self.wrist_pot)
        wpilib.LiveWindow.addActuator(self.name, "Wrist PID", self.wrist_controller)

        #Setup tasks
        self.add_task(self.teleop_loop())
        self.add_task(self.run_loop())

    def get_pid_in(self):
        value = self.elevator_pot.get()
        return value

    def set_pid_out(self, value):
        self.elevator_motor.set(value)

    @asyncio.coroutine
    def teleop_loop(self):
        while True:
            yield from yeti.get_event("teleoperated").wait()
            claw_tgt = self.state_data["claw_open"]
            elevator_tgt = self.state_data["elevator_pos"]
            wrist_tgt = self.state_data["wrist_pos"]
            claw_close_button = self.joystick.getRawButton(4)
            claw_open_button = self.joystick.getRawButton(2)
            elevator_up_button = self.joystick.getRawButton(5)
            elevator_down_button = self.joystick.getRawButton(3)
            wrist_up_button = self.joystick.getRawButton(6)
            wrist_down_button = self.joystick.getRawButton(7)

            if claw_close_button:
                claw_tgt = False
            elif claw_open_button:
                claw_tgt = True

            if elevator_up_button:
                elevator_tgt = 1
            elif elevator_down_button:
                elevator_tgt = 0

            if wrist_up_button:
                wrist_tgt = -45
            elif wrist_down_button:
                wrist_tgt = 0

            control_data = {"claw_open": claw_tgt, "elevator_pos": elevator_tgt, "wrist_pos": wrist_tgt}
            self.control_datastream.set(control_data)
            yield from asyncio.sleep(.03)

    @asyncio.coroutine
    def run_loop(self):
        while True:
            yield from yeti.get_event("enabled").wait()
            control_data = self.control_datastream.get(self.control_data_default)
            if control_data["claw_open"]:
                self.claw_motor.set(-1)

            else:
                self.claw_motor.set(1)
            self.state_data["claw_open"] = control_data["claw_open"]
            self.state_data["elevator_pos"] = control_data["elevator_pos"]
            self.state_data["wrist_pos"] = control_data["wrist_pos"]
            self.elevator_controller.setSetpoint(control_data["elevator_pos"])
            self.wrist_controller.setSetpoint(control_data["wrist_pos"])
            #self.pid_controller.calculate()
            yield from asyncio.sleep(.2)
