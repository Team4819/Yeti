import yeti
import wpilib
import asyncio

class Claw(yeti.Module):

    control_data_default = {"claw_open": False, "elevator_pos": 0, "wrist_pos": 0}
    state_data = {"claw_open": False, "elevator_pos": 0, "wrist_pos": 0}

    def module_init(self):
        self.joystick = wpilib.Joystick(0)
        self.claw_motor = wpilib.Victor(7)
        self.claw_contact = wpilib.DigitalInput(5)

        #Get the control datastream
        self.control_datastream = yeti.get_datastream("claw_control")

        #Get the state datastream
        self.state_datastream = yeti.get_datastream("claw_state")
        self.state_datastream.set(self.state_data)

        #Get the PID controller
        self.pid_controller = wpilib.PIDController(18, 0.2, 0, self.get_pid_in, self.set_pid_out)


        # Let's show everything on the LiveWindow
        wpilib.LiveWindow.addActuator(self.name, "Claw Motor", self.claw_motor)
        wpilib.LiveWindow.addActuator(self.name, "Claw Limit Switch", self.claw_contact)

        self.elevator_motor = wpilib.Victor(5)

        self.elevator_pot = wpilib.AnalogPotentiometer(2)    # defaults to meters

        # Let's show everything on the LiveWindow
        wpilib.LiveWindow.addActuator(self.name, "Elevator Motor", self.elevator_motor)
        wpilib.LiveWindow.addSensor(self.name, "Elevator Pot", self.elevator_pot)
        wpilib.LiveWindow.addActuator(self.name, "Elevator PID", self.pid_controller)

        #Setup tasks
        self.add_task(self.teleop_loop())
        self.add_task(self.run_loop())

    def get_pid_in(self):
        return self.elevator_pot.get()

    def set_pid_out(self, value):
        self.elevator_motor.set(value)

    @asyncio.coroutine
    def teleop_loop(self):
        yield from yeti.get_event("teleoperated").wait()
        elevator_tgt = self.joystick.getZ()
        claw_tgt = self.state_data["claw_open"]
        close_button = self.joystick.getButton(5)
        open_button = self.joystick.getButton(3)
        if close_button:
            claw_tgt = False
        elif open_button:
            claw_tgt = True
        control_data = {"claw_open": claw_tgt, "elevator_pos": elevator_tgt, "wrist_pos": 0}
        self.control_datastream.set(control_data)
        yield from asyncio.sleep(.03)

    @asyncio.coroutine
    def run_loop(self):
        yield from yeti.get_event("enabled").wait()
        control_data = self.control_datastream.get(self.control_data_default)
        if control_data["claw_open"]:
            self.claw_motor.set(-1)
        else:
            self.claw_motor.set(1)
        self.pid_controller.setSetpoint(control_data["elevator_pos"])
        yield from asyncio.sleep(.03)
