import asyncio
import logging


class Module(object):
    name = "module"
    event_loop = None

    def __init__(self):
        self.name = self.__class__.__name__
        self.logger = logging.getLogger('yeti.' + self.name)
        self.tasks = list()


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
        task.add_done_callback(self.handle_result)
        self.tasks.append(task)

    def base_exception_handler(self, future):
        return future.result()

    exception_handler = base_exception_handler

    def handle_result(self, fut):
        if fut.exception():
            self.exception_handler(fut)
