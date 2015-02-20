import asyncio
import logging
import functools
import inspect

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
        self.tagged_objects = dict()
        self.add_hook("end_task", self._finish_task)
        self.add_hook("init", self.module_init)
        self.add_hook("init", self.classify_objects)
        self.add_hook("init", self.autostart_coroutines)
        self.add_hook("deinit", self.module_deinit)

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
        try:
            self.call_hook("init", supress_exceptions=False)
        except Exception as e:
            self.call_hook("exception", e)

        self.logger.info("Loaded Module {}.".format(self.name))

    def stop(self):
        """
        This is used to stop module operation. It cancels all running coroutines and calls the `module_deinit`
        hook to stop everything
        """
        self.call_hook("deinit")
        for task in self.tasks:
            task.cancel()
        self.event_loop = None
        self.logger.info("Unloaded Module {}".format(self.name))

    def start_coroutine(self, coroutine):
        """
        Schedule an asyncio coroutine in the module's event loop, and add hooks to handle coroutine failure.

        :param coroutine: The asyncio coroutine to schedule.
        """
        if self.event_loop is None:
            raise ValueError("No event loop setup")
        task = asyncio.async(coroutine)
        task.add_done_callback(functools.partial(self.call_hook, "end_task"))
        self.add_hook("deinit", task.cancel)
        self.call_hook("add_task", task)
        self.tasks.append(task)

    def classify_objects(self):
        for name, obj in inspect.getmembers(self):
            tags = list_tags(obj)
            for tag in tags:
                if tag not in self.tagged_objects:
                    self.tagged_objects[tag] = list()
                self.tagged_objects[tag].append(obj)

    def autostart_coroutines(self):
        for coro in self.tagged_objects.get("autorun", []):
            self.start_coroutine(coro())

    def _finish_task(self, fut):
        try:
            if fut.exception():
                if not self.call_hook("exception", fut.exception()):
                    return fut.result()
        except asyncio.CancelledError:
            pass

def add_tag(obj, tag_name, tag_data=True):
    """
    A helper function that adds a classification tag to the given object

    :param obj: The object to add a classification to.
    :param tag_name: The name of tag to add.

    :returns: obj with a classification tag.
    """

    if not hasattr(obj, "tags"):
        obj.tags = {}
    obj.tags[tag_name] = tag_data
    return obj

def list_tags(obj):
    """
    :returns: The dictionary of tags in a given object.
    """
    if hasattr(obj, "tags"):
        return obj.tags
    else:
        return {}

def copy_tags(source, target):
    """
    A helper function that copies all tags from one object to another.
    """
    if not hasattr(target, "tags"):
        target.tags = {}
    target.tags.update(list_tags(source))

def autorun_coroutine(func):
    """
    A decorator that sets the coroutine to schedule automatically upon module init.
    """
    return add_tag(func, "autorun")