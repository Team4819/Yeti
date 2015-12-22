import asyncio
import logging
import inspect

from .engine import get_engine


class Module:
    """
    Provide an interface for bundling and externally controlling asyncio coroutines.
    This is intended to be subclassed to create a module for a specific purpose.
    """
    name = "module"
    alive = True

    def __init__(self, engine=None):
        # Get engine for thread if none provided
        if engine is None:
            engine = get_engine()
        self.engine = engine

        # Get class name and logger
        self.name = self.__class__.__name__
        self.logger = logging.getLogger('yeti.' + self.name)

        # Get embedded modules
        for mod_id in self.engine.embedded_modules:
            setattr(self, mod_id, self.engine.get_module(mod_id))

        self.cached_tags = {}
        self.tasks = []

    def start(self):
        self.module_init()

        # Start the coroutines tagged with "autorun".
        for method in self.get_tagged_methods("autorun"):
            self.start_coroutine(method())

        self.logger.info("Started Module {}.".format(self.name))

    def module_init(self):
        """User-overriden for initializing the module."""
        self.logger.warn("module_init: Override me!")

    def module_deinit(self):
        """Used for freeing any used resources."""
        pass

    async def stop(self):
        """
        This is used to stop module operation. It cancels all running tasks and calls `module_deinit`
        """
        for task in self.tasks:
            task.cancel()
        try:
            self.module_deinit()
        except Exception as e:
            self.logger.exception(e)
        self.logger.info("Stopped Module {}".format(self.name))
        self.alive = False

    def start_coroutine(self, coroutine):
        """
        Schedule an asyncio coroutine in the module's event loop, and add hooks to handle coroutine failure.

        :param coroutine: The asyncio coroutine to schedule.
        """
        task = asyncio.async(coroutine)
        task.add_done_callback(self._catch_exceptions)
        self.tasks.append(task)

    def get_tagged_methods(self, tag):
        if tag not in self.cached_tags:
            self.cached_tags[tag] = []
            for name, obj in inspect.getmembers(self):
                if name.startswith(tag) \
                        or (callable(obj) and hasattr(obj, "tags") and tag in obj.tags):
                    self.cached_tags[tag].append(obj)
        return self.cached_tags[tag]

    def _catch_exceptions(self, fut):
        try:
            if fut.exception():
                return fut.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if self.alive:
                self.logger.error(e)
                self.engine.fail_module(self)

    def is_alive(self):
        return self.alive

def autorun(func):
    """
    A decorator that sets the coroutine to schedule automatically upon module init.
    """
    if not hasattr(func, "tags"):
        func.tags = []
    func.tags.append("autorun")
    return func

def singleton(func):
    """
    A decorator that ensures only one instance of a coroutine is running at any time.
    """
    func.lock = asyncio.Lock()

    async def func_wrapper(self, *args, **kwargs):
        if func.lock.locked():
            return

        async with func.lock:
            await func(self, *args, **kwargs)

    return func_wrapper
