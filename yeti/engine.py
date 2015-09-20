import threading
import importlib
import inspect
import asyncio
import logging
import sys
import yaml

_engine_instances = dict()

def set_engine(engine):
    """
    Sets the context for the current thread.

    :param context: An instance of Engine to be saved
    """
    _engine_instances[threading.current_thread()] = engine

def get_engine():
    """
    :returns: the engine set for the current thread.
    """
    return _engine_instances[threading.current_thread()]

class Engine:
    """
    This hosts an asyncio event loop in a thread, and contains mechanisms for loading and running modules.
    """
    event_loop = None
    _thread = None

    def __init__(self):
        self.loaded_modules = {}
        self.running_modules = {}
        self.failed_modules = []

        self.module_dirs = [""]
        self.module_sets = {}
        self.enabled_modules = []

        self.event_loop = asyncio.new_event_loop()
        asyncio.async(self._start(), loop=self.event_loop)
        self.logger = logging.getLogger(name="yeti." + self.__class__.__name__)

    def thread_coroutine(self, coroutine, logger=None):
        """
        Schedules coroutine to be run in the engine's event loop.
        This function is thread-safe.

        :param coroutine: The coroutine to schedule
        """
        if logger is None:
            logger = self.logger
        self.event_loop.call_soon_threadsafe(asyncio.async, self._error_net(coroutine, logger))

    @asyncio.coroutine
    def _error_net(self, coro, log):
        try:
            yield from coro
        except Exception as e:
            self.logger.exception(e)

    # -----------------Engine start/stop---------------------------

    def spawn_thread(self):
        """Spawns a new thread and runs :meth:`.run_forever` in it."""
        if self._thread is None:
            self._thread = threading.Thread(target=self.run_forever)
            self._thread.start()

    def run_forever(self):
        """
        Sets the engine for the current thread, and runs the engine's event loop forever.
        """
        set_engine(self)
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_forever()

    def run_for(self, time):
        """
        Sets the engine for the current thread, and runs the engine's event loop for the specified duration.

        :param time: The time in seconds to run the event loop for.
        """
        set_engine(self)
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_until_complete(asyncio.sleep(time))

    @asyncio.coroutine
    def _start(self):
        for mod_id in self.enabled_modules:
            try:
                yield from self.start_module(mod_id)
            except Exception as e:
                self.logger.exception(e)

    def stop(self):
        """
        Schedules :meth:`._stop_coroutine` to be run in the engine's event loop.
        This method is thread-safe.
        """
        self.thread_coroutine(self._stop_coroutine)

    @asyncio.coroutine
    def _stop_coroutine(self):
        """
        Unloads all modules and stops the event loop.
        This method is a coroutine.
        """
        for modname in self.loaded_modules:
            yield from self.stop_module(modname)
        self.event_loop.stop()

    # -------------------Config reading---------------------------

    def load_config(self, filename):
        # Read yaml file
        file = open(filename)
        data = yaml.load(file)
        file.close()

        # Save config data
        self.module_sets.update(data.get("module_sets", {}))
        self.enabled_modules.extend(data.get("enabled", []))
        self.module_dirs.extend(data.get("module_dirs", []))

    # -------------------Module Controls---------------------------

    @asyncio.coroutine
    def reload_module(self, module):
        """
        Reload the python module at pymod_path, re-starting any child yeti modules
        """
        mod_path, mod_object = self._get_module(module)

        # Stop the running module
        yield from self.stop_module(mod_path)

        # Re-load the python module
        for mod_dir in self.module_dirs:
            if mod_dir != "":
                real_path = ".".join([mod_dir, mod_path])
            else:
                real_path = mod_path
            if real_path in sys.modules:
                importlib.reload(sys.modules[real_path])

        # Re-start the module
        yield from self.start_module(mod_path)

    @asyncio.coroutine
    def start_module(self, mod_id, mod_class=None, mod_object=None):
        """
        Creates a module object and adds it to running_modules
        """
        if mod_id in self.running_modules:
            return

        if mod_id in self.module_sets:
            # mod_id is a module set, get the first module that hasn't failed on us
            mod_set = self.module_sets[mod_id]
            for mod_path in mod_set:
                if mod_path not in self.failed_modules:
                    try:
                        yield from self._start_module(mod_path, mod_class, mod_object)
                        break
                    except Exception as e:
                        self.failed_modules.append(mod_path)
                        self.logger.exception(e)
            else:
                raise RuntimeError("No module paths in module set '{}' that haven't failed.".format(mod_id))
        else:
            try:
                yield from self._start_module(mod_id, mod_class, mod_object)
            except Exception as e:
                self.failed_modules.append(mod_id)
                raise e

    @asyncio.coroutine
    def _start_module(self, mod_path, mod_class=None, mod_object=None):
        if mod_object is None:
            if mod_class is None:
                # Get python module
                for disc_path in self.module_dirs:
                    try:
                        if disc_path == "":
                            real_path = mod_path
                        else:
                            real_path = ".".join([disc_path, mod_path])
                        if real_path in sys.modules:
                            pymod = sys.modules[real_path]
                        else:
                            pymod = importlib.import_module(real_path)
                    except ImportError as e:
                        if e.msg == "No module named '{}'".format(real_path):
                            continue
                        raise e
                    else:
                        break
                else:
                    raise ImportError("Failed to find module {} in any discovery paths.".format(mod_path))
                # Get module class
                for name, obj in inspect.getmembers(pymod):
                    if inspect.isclass(obj) and hasattr(obj, "stop"):
                        mod_class = obj
                        break
                else:
                    raise RuntimeError("No compatible module class found in " + mod_path)

            mod_object = mod_class(self)
            try:
                mod_object.start()
            except Exception as e:
                yield from mod_object.stop()
                raise e

        self.running_modules[mod_path] = mod_object

    @asyncio.coroutine
    def stop_module(self, module):
        mod_path, mod_object = self._get_module(module)
        yield from mod_object.stop()
        if mod_path in self.running_modules:
            del(self.running_modules[mod_path])

    @asyncio.coroutine
    def fail_module(self, module, replace_mod=True):
        mod_path, mod_object = self._get_module(module)
        yield from self.stop_module(mod_path)
        self.failed_modules.append(mod_path)
        if not replace_mod:
            return
        for set_id in self.module_sets:
            mod_set = self.module_sets[set_id]
            if mod_path in mod_set:
                index = mod_set.indexOf(mod_path)
                if index+1 < len(mod_set):
                    yield from self.start_module(mod_set[index+1])
                    return

    def get_tagged_methods(self, tag):
        tags = []
        for mod in self.running_modules:
            tags.extend(self.running_modules[mod].get_tagged_methods(tag))
        return tags

    @asyncio.coroutine
    def run_tagged_methods(self, tag, *args, **kwargs):
        for mod in self.running_modules:
            mod_obj = self.running_modules[mod]
            for method in mod_obj.get_tagged_methods(tag):
                if asyncio.iscoroutinefunction(method):
                    mod.start_coroutine(method(*args, **kwargs))
                else:
                    method(*args, **kwargs)

    def get_module(self, mod_id):
        return GhostModule(self, mod_id)

    def _get_module(self, module):
        if isinstance(module, str):
            mod_id = module
            if mod_id in self.module_sets:
                for mod_path in self.module_sets[mod_id]:
                    if mod_path in self.running_modules:
                        break
                else:
                    raise ValueError("No running modules in module_set {}".format(mod_id))
            else:
                mod_path = mod_id
            mod_object = self.running_modules[mod_path]
        else:
            mod_object = module
            for mod_path in self.running_modules:
                if self.running_modules[mod_path] is mod_object:
                    break
            else:
                raise ValueError("{} not in running modules".format(mod_object))
        return mod_path, mod_object

class GhostModule:
    def __init__(self, engine, mod_id):
        self.mod_id = mod_id
        self.engine = engine
        self.mod_obj = None

    def __getattr__(self, item):
        if self.mod_obj is None or not self.mod_obj.alive:
            _, self.mod_obj = self.engine._get_module(self.mod_id)
        return getattr(self.mod_obj, item)