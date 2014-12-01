from threading import Thread
import logging
import asyncio
import wpilib
from . import events

class AsyncioModule(object):
    module_thread = None
    name = "module"
    _run_target = None
    event_loop = None

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

    def stop(self):
        for task in self.tasks:
            task.cancel()
        self.event_loop.stop()

    def add_task(self, function):
        if self.event_loop is not None:
            self.tasks.append(asyncio.Task(function))

    def _run_loop(self):
        try:
            #Get the event loop
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)

            #Initialize the module
            self.module_init()

            #Loop while we have tasks.
            self.event_loop.run_until_complete(asyncio.wait(self.tasks))
            self.event_loop.close()

        finally:
            try:
                self.module_deinit()
            except Exception as e:
                logging.error(e)

        print("Clean termination of module {}".format(self.name))

