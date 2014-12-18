import threading
import asyncio

from .hook_server import HookServer


_contexts = dict()

def set_context(context):
    """
    :param context: An instance of Context to be saved
    Sets the context for the current thread.
    """
    _contexts[threading.current_thread()] = context

def get_context():
    """
    :returns the context set for that thread.
    """
    return _contexts[threading.current_thread()]

class Context(HookServer):
    """
    This hosts an asyncio event loop in a thread, and contains mechanisms for loading and unloading modules.
    """
    event_loop = None
    _thread = None

    def __init__(self):
        super().__init__()
        self.loaded_modules = dict()
        self.interface_data = dict()
        self.interface_data_lock = threading.RLock()
        self.event_loop = asyncio.new_event_loop()

    def thread_coroutine(self, coroutine):
        """
        :param coroutine: The coroutine to schedule
        Schedules coroutine to be run in the context's event loop.
        This function is thread-safe.
        """
        self.event_loop.call_soon_threadsafe(asyncio.async, coroutine)

    def get_event_loop(self):
        """
        :returns The context's event loop
        """
        return self.event_loop

    def get_interface_data(self, interface_id):
        """
        :param interface_id: The string identifier for the data tuple to return
        :returns A data tuple of type (:class:dict() , :class:threading.RLock())
        Returns a data tuple stored for the identifier interface_id, creating one if necessary.
        """
        with self.interface_data_lock:
            if interface_id not in self.interface_data:
                self.interface_data[interface_id] = (dict(), threading.RLock())
            data = self.interface_data[interface_id]
        return data

    def start(self):
        """Spawns a new thread and runs :meth:run_forever in it."""
        if self._thread is None:
            self._thread = threading.Thread(target=self.run_forever)
            self._thread.start()

    def run_forever(self):
        """
        Sets the context for the current thread, and runs the context's event loop forever.
        """
        set_context(self)
        asyncio.set_event_loop(self.event_loop)
        self.call_hook("context_start", self)
        self.event_loop.run_forever()

    def run_for(self, time):
        """
        :param time: The time in seconds to run the event loop for.
        Sets the context for the current thread, and runs the context's event loop for the specified duration.
        """
        set_context(self)
        asyncio.set_event_loop(self.event_loop)
        self.call_hook("context_start", self)
        self.event_loop.run_until_complete(asyncio.sleep(time))

    def stop(self):
        """
        Schedules :meth:stop_coroutine to be run in the context's event loop.
        This method is thread-safe.
        """
        self.thread_coroutine(self.stop_coroutine)

    @asyncio.coroutine
    def stop_coroutine(self):
        """
        Unloads all modules and stops the event loop.
        This method is a coroutine.
        """
        for modname in self.loaded_modules:
            yield from self.unload_module_coroutine(modname)
        self.call_hook("context_stop", self)
        self.event_loop.stop()

    def load_module(self, module):
        """
        :param module: The module object to load into the context.
        Schedules load_module_coroutine to be run in the context's event loop.
        This method is thread-safe.
        """
        self.thread_coroutine(self.load_module_coroutine(module))

    @asyncio.coroutine
    def load_module_coroutine(self, module):
        """
        :param module: The module object to load into the context.
        Loads module into the context, and errors if we already have one with that name. Triggers module.init().
        """
        if module.name in self.loaded_modules:
            raise ValueError("Already have a module with name {} in this context, cannot add another.")
        self.loaded_modules[module.name] = module
        module.init(loop=self.event_loop)
        self.call_hook("module_load", self.loaded_modules[module])

    def unload_module(self, module_name):
        """
        :param module_name: The the name of the module to be unloaded from the context.
        Schedules unload_module_coroutine to be run in the context's event loop.
        This method is thread-safe.
        """
        self.thread_coroutine(self.unload_module(module_name))

    @asyncio.coroutine
    def unload_module_coroutine(self, module_name):
        """
        :param module_name: The name of the module to be unloaded the context.
        Unloads module_name from the context. Triggers module.deinit().
        """
        if module_name not in self.loaded_modules:
            raise ValueError("Module {} not loaded.".format(module_name))
        self.loaded_modules[module_name].deinit()
        self.call_hook("module_unload", self.loaded_modules[module_name])
        del(self.loaded_modules[module_name])