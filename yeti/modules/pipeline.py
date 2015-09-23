import yeti
import wpilib
import asyncio

class Pipeline(yeti.Module):
    """
    A built-in module providing synchronized robot sensor, state, and control updates.
    """
    # Default run frequency is 20 cycles per second
    cycles_per_sec = 20

    def module_init(self):
        self.state = {}
        self.control = {}
        self.sensor = {}
        self.output = {}
        self.sensor_polls = {}
        self.output_polls = {}

    def add_sensor_poll(self, poll, key, value_init=None, deriv_order=0):
        self.sensor_polls[key] = {
            "poll": poll,
            "deriv_order": deriv_order,
        }
        if value_init is not None:
            self.sensor[key] = value_init

    def add_output_poll(self, poll, key):
        self.output_polls[key] = poll

    def set_frequency(self, cycles_per_sec):
        self.cycles_per_sec = cycles_per_sec

    @yeti.autorun
    @asyncio.coroutine
    def main_loop(self):
        last_cycle_timestamp = wpilib.Timer.getFPGATimestamp()
        while True:
            yield from asyncio.sleep(1/self.cycles_per_sec)

            # Get delta time
            current_cycle_timestamp = wpilib.Timer.getFPGATimestamp()
            delta_time = current_cycle_timestamp - last_cycle_timestamp
            last_cycle_timestamp = current_cycle_timestamp

            # Get predicted sensor data
            last_sensor = self.sensor.copy()
            for method in self.engine.get_tagged_methods("pipeline_sensor_prediction"):
                self.sensor.update(method(delta_time, last_sensor.copy(), self.output))

            # Poll sensors, overwriting any predicted data
            defective_sensors = []
            for key in self.sensor_polls:
                try:
                    last_value = self.sensor.get(key, [0]*self.sensor_polls[key]["deriv_order"])
                    value = self.sensor[key] = self.sensor_polls[key]["poll"]()
                    for order in range(self.sensor_polls[key]["deriv_order"]):
                        value[order+1] = (value[order] - last_value[order])/delta_time
                except Exception as e:
                    self.logger.exception(e)
                    defective_sensors.append(key)
            for key in defective_sensors:
                del(self.sensor_polls[key])

            # Perform state update,
            last_state = self.state.copy()
            for method in self.engine.get_tagged_methods("pipeline_state_update"):
                self.state.update(method(delta_time, last_state.copy(), self.sensor))

            # Perform control update
            for method in self.engine.get_tagged_methods("pipeline_control_update"):
                self.output.update(method(delta_time, self.state, self.control))

            # Poll sensors, overwriting any predicted data
            defective_outputs = []
            for key in self.output_polls:
                try:
                    if key in self.output:
                        self.output_polls[key](self.output[key])
                except Exception as e:
                    self.logger.exception(e)
                    defective_outputs.append(key)
            for key in defective_outputs:
                del(self.output_polls[key])