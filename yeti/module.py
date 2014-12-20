import asyncio
import logging
import functools

from .hook_server import HookServer


class Module(HookServer):
    """
    Provide an interface for bundling and externally controlling asyncio coroutines.
    This is intended to be subclassed to create a module for a specific purpose.
    """
    name = "module"
    event_loop = None

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__
        self.logger = logging.getLogger('yeti.' + self.name)
        self.tasks = list()
        self.add_hook("end_task", self._finish_task)
        self.add_hook("module_init", self.module_init)
        self.add_hook("module_deinit", self.module_deinit)

    def module_init(self):
        """A default `module_init` hook used for initializing the module, and starting any coroutines."""
        self.logger.warn("module_init: Override me!")

    def module_deinit(self):
        """A default `module_deinit` hook used for freeing any used resources."""
        pass

    def start(self, loop=None):
        """
        Start module operation. It configures the asyncio event loop to use for runtime, and
        calls the `module_init` hook to get things running.

        :param loop: An optional event loop to use for module run.
        """
        if loop is None:
            self.event_loop = asyncio.get_event_loop()
        else:
            self.event_loop = loop
        self.call_hook("module_init")
        self.logger.info("Finished module init.")

    def stop(self):
        """
        This is used to stop module operation. It cancels all running coroutines and calls the `module_deinit`
        hook to stop everything
        """
        for task in self.tasks:
            task.cancel()
        self.event_loop = None
        self.call_hook("module_deinit")
        self.logger.info("Finished module deinit.")

    def add_task(self, coroutine):
        """
        Schedule an asyncio coroutine in the module's event loop, and add hooks to handle coroutine failure.

        :param coroutine: The asyncio coroutine to schedule.
        """
        if self.event_loop is None:
            raise ValueError("No event loop setup")
        task = asyncio.async(coroutine)
        task.add_done_callback(functools.partial(self.call_hook, "end_task"))
        self.add_hook("module_deinit", task.cancel)
        self.call_hook("add_task", task)
        self.tasks.append(task)

    def _finish_task(self, fut):
        if fut.exception():
            if not self.call_hook("exception", fut.exception()):
                return fut.result()
