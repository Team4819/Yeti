from threading import Thread
import logging
import wpilib


class RunCondition(object):
    def is_met(self, current_time):
        """
        :returns Whether the condition is met, and the time of the next call.
        """

        return False, current_time + 1


class TimeCondition(RunCondition):
    """A simple run condition that is met after a time delay"""
    target_time = 0

    def __init__(self, delay):
        self.target_time = wpilib.Timer.getFPGATimestamp() + delay

    def is_met(self, current_time):
        time_delta = self.target_time - current_time
        return time_delta < .01, self.target_time


class Task(object):

    last_run_time = None
    running = True

    def __init__(self, target, initial_run_conditions):
        self.target = target
        self.last_run_time = None
        self.populate_conditions(initial_run_conditions)

    def start(self):
        self.running = True

    def check_conditions(self, current_time):
        next_poll = current_time + 10
        met = True
        for condition in self.current_run_conditions:
            condition_met, condition_delay = condition.is_met(current_time)
            next_poll = min(next_poll, condition_delay)
            if not condition_met:
                met = False
        return met, next_poll

    def populate_conditions(self, condition_input):
        if not hasattr(condition_input, "__iter__"):
            condition_input = [condition_input]

        self.current_run_conditions = []

        for output in condition_input:
            if hasattr(output, "is_met"):
                self.current_run_conditions.append(output)
            else:
                self.current_run_conditions.append(TimeCondition(output))

    def iterate(self):
        """
        Runs an iteration of the task and gets the next loop time.
        :returns the maximum time to wait for the next loop iteration.
        """
        if not self.running:
            return 10

        current_time = wpilib.Timer.getFPGATimestamp()

        met, next_poll = self.check_conditions(current_time)

        if met:
            try:
                #Figure out what to send to the target, as we can't send a real value
                # if it hasn't been run yet
                value_to_send = None
                if self.last_run_time is not None:
                    value_to_send = current_time - self.last_run_time

                #Run the target until another yield is encountered.
                yield_output = self.target.send(value_to_send)

                self.populate_conditions(yield_output)

                next_poll, met = self.check_conditions(current_time)

                #Save the last run time
                self.last_run_time = current_time
            except StopIteration:
                self.running = False
                return 10

        return next_poll


class Module(object):
    module_thread = None
    name = "module"
    _run_target = None

    def __init__(self):
        self.tasks = list()
        self.name = self.__class__.__name__
        self._run_target = self._run_loop

    def module_init(self):
        pass

    def module_deinit(self):
        pass

    def start(self):
        self.module_thread = Thread(target=self._run_target)
        self.module_thread.start()
        print("Started module {}".format(self.name))

    def add_task(self, function, initial_run_condition):
        self.tasks.append(Task(function, initial_run_condition))

    def _run_loop(self):
        try:
            #Initialize the module
            self.module_init()

            #Loop while we have tasks.
            while len(self.tasks) != 0:
                next_time = wpilib.Timer.getFPGATimestamp() + 5
                for task in self.tasks[:]:
                    if task.running:
                        task_next_delay = task.iterate()
                        next_time = min(next_time, task_next_delay)
                    else:
                        self.tasks.remove(task)
                next_delay = next_time - wpilib.Timer.getFPGATimestamp()
                if next_delay < .1:
                    next_delay = .1
                wpilib.Timer.delay(next_delay)
        finally:
            try:
                self.module_deinit()
            except Exception as e:
                logging.error(e)

        print("Clean termination of module {}".format(self.name))
