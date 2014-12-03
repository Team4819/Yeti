import threading
import asyncio


class Context(object):
    event_loop = None
    thread = None

    def __init__(self):
        self.loaded_modules = dict()
        self.data = dict()
        self.event_loop = asyncio.new_event_loop()
        self.event_loop.set_debug(True)

    def get_event_loop(self):
        return self.event_loop

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self._run_loop)
            self.thread.start()

    def stop(self):
        self.event_loop.call_soon_threadsafe(self._stop)

    def _stop(self):
        for module in self.loaded_modules:
            self.loaded_modules[module]._deinit()
        self.event_loop.stop()

    def _run_loop(self):
        asyncio.set_event_loop(self.event_loop)
        #self.event_loop.set_exception_handler(self.exception_handler)
        self.event_loop.run_forever()
        self.event_loop.close()

    def _add_module(self, module):
        if module.name in self.loaded_modules:
            raise ValueError("Already have a module with name {} in this context, cannot add another.")
        module.bind_context(self)
        self.loaded_modules[module.name] = module
        self.event_loop.call_soon(module._init)

    def add_module(self, module):
        self.event_loop.call_soon_threadsafe(self._add_module, module)

    def exception_handler(self, loop, context):
        for module in self.loaded_modules:
            if module.is_own_task(context["handle"]) and hasattr(module, "exception_handler"):
                module.exception_handler()
                break
        else:
            loop.default_exception_handler(context)
