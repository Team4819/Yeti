import threading
import asyncio

contexts = dict()

def set_context(context):
    contexts[threading.current_thread()] = context

def get_context():
    return contexts[threading.current_thread()]

class Context(object):
    event_loop = None
    thread = None

    def __init__(self):
        self.loaded_modules = dict()
        self.datastore = dict()
        self.datastore_lock = threading.RLock()
        self.event_loop = asyncio.new_event_loop()

    def set_debug(self, debug):
        self.event_loop.set_debug(debug)

    def thread_coroutine(self, co):
        self.event_loop.call_soon_threadsafe(asyncio.async, co)

    def get_event_loop(self):
        return self.event_loop

    def get_data(self, key):
        with self.datastore_lock:
            if key not in self.datastore:
                self.datastore[key] = (dict(), threading.RLock())
            data = self.datastore[key]
        return data

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self.run)
            self.thread.start()

    def stop(self):
        self.event_loop.call_soon_threadsafe(self._stop)

    def _stop(self):
        for module in self.loaded_modules:
            self.loaded_modules[module]._deinit()
        self.event_loop.stop()

    def run(self):
        set_context(self)
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_forever()

    def run_for(self, time):
        set_context(self)
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_until_complete(asyncio.sleep(time))

    @asyncio.coroutine
    def add_module_coroutine(self, module):
        if module.name in self.loaded_modules:
            raise ValueError("Already have a module with name {} in this context, cannot add another.")
        module.bind_context(self)
        self.loaded_modules[module.name] = module
        module._init()

    def add_module(self, module):
        self.thread_coroutine(self.add_module_coroutine(module))

    @asyncio.coroutine
    def unload_module_coroutine(self, modname):
        if modname not in self.loaded_modules:
            raise ValueError("Module {} not loaded.".format(modname))
        self.loaded_modules[modname]._deinit()
        del(self.loaded_modules[modname])

    def unload_module(self, module):
        self.thread_coroutine(self.unload_module(module))

