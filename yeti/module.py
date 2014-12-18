import asyncio
import logging
from functools import partial

from .hook_server import HookServer


class Module(HookServer):
    name = "module"
    event_loop = None

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__
        self.logger = logging.getLogger('yeti.' + self.name)
        self.tasks = list()
        self.add_hook("end_task", self.handle_result)


    def init(self, loop=None):
        if loop is None:
            self.event_loop = asyncio.get_event_loop()
        else:
            self.event_loop = loop
        self.module_init()
        self.logger.info("Finished module init.")

    def deinit(self):
        for task in self.tasks:
            task.cancel()
        self.module_deinit()
        self.logger.info("Finished module deinit.")

    def module_init(self):
        pass

    def module_deinit(self):
        pass

    def add_task(self, function):
        if self.event_loop is None:
            raise ValueError("No event loop setup")
        task = asyncio.async(function)
        task.add_done_callback(partial(self.call_hook, "end_task"))
        self.call_hook("add_task", task)
        self.tasks.append(task)


    def handle_result(self, fut):
        if fut.exception():
            if not self.call_hook("exception", fut.exception()):
                return fut.result()
