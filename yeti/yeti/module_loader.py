import logging
import os
import imp
import traceback
import inspect
import asyncio

class ModuleLoadError(Exception):
    """This error is for errors during module load"""
    def __init__(self, name, message):
        super().__init__(name + ": " + message)


class ModuleUnloadError(Exception):
    """This error is for errors during module unload"""
    def __init__(self, name, message):
        super().__init__(name + ": " + message)


class ModuleLoader(object):

    def __init__(self):

        self.fallback_list = list()
        """The list of fallback modules to use on case of failure"""

        self.fallback_index = 0
        """The current modules index on the fallback list"""

        self.module_path = ""
        """The loaded modules filename"""

        self.module_name = ""
        """The loaded modules subsystem name"""

        self.module_object = None
        """The module object"""

        self.module_import = None
        """The imported module file"""

        self.module_context = None
        """The context use for the module."""

    def set_context(self, context):
        self.module_context = context

    def get_context(self):
        if self.module_context is None:
            raise ValueError("No context set.")
        return self.module_context

    def get_module(self):
        return self.module_object

    @asyncio.coroutine
    def reload_coroutine(self):
        yield from self.load()

    def reload(self):
        self.get_context().thread_coroutine(self.reload_coroutine())

    def add_fallback(self, fallback):
        self.fallback_list.append(fallback)

    @asyncio.coroutine
    def load_coroutine(self, module_path=None):
        """
        Load a module into the wrapper, either from a name, or use the existing fallback_list and fallback_index
        """

        #Start by unloading any previously loaded module
        yield from self.unload_coroutine()

        #Setup module fallback lists

        #If a module was actually specified, try to find it in fallback_list, otherwise,
        # wipe fallback_list and add module_path
        if module_path is not None:
            if module_path in self.fallback_list:
                self.fallback_index = self.fallback_list.index(module_path)
            else:
                self.fallback_list = [module_path]
                self.fallback_index = 0

        #Loop through fallback_list and try to find a module that will load.
        while True:

            #Do we have any more to try?
            if self.fallback_index >= len(self.fallback_list):
                raise ModuleLoadError(self.module_name, "No files left to try and load in the fallback list")

            #Lets try this module, the one selected by fallback_index
            file_to_load = self.fallback_list[self.fallback_index]
            try:

                logging.info("Loading " + file_to_load)

                if file_to_load == self.module_path:
                    #This is the same file we have already loaded! just wipe the cache, if necessary, and reload it!
                    path = getattr(self.module_import, "__cached__")
                    if os.path.exists(path):
                        os.remove(path)
                    self.module_import = imp.reload(self.module_import)
                else:
                    #Load the python file from scratch
                    self.module_import = __import__(file_to_load, fromlist=[''])

                #Get the module class
                module_class = None
                for name, obj in inspect.getmembers(self.module_import):
                    if inspect.isclass(obj):
                        module_class = obj
                        break

                #Initialize the actual module object
                self.module_object = module_class()

                #Get the module's name and file name
                self.module_name = self.module_object.name
                self.module_path = file_to_load

                #Setup exception handler
                self.module_object.exception_handler = self.exception_handler

                #Add module to the current context:
                yield from self.module_context.add_module_coroutine(self.module_object)

                #Yay, we must have been successful!
                break

            except Exception as e:
                #Oops, something happened. We must try the next one on the fallback list!
                logging.error("Error loading module: " + file_to_load + ": " + str(e) + "\n" + traceback.format_exc())
                self.fallback_index += 1

    def load(self, module_path=None):
        self.get_context().thread_coroutine(self.load_coroutine(module_path))

    @asyncio.coroutine
    def unload_coroutine(self):
        """Unload the currently loaded module"""
        if self.module_object is not None:
            yield from self.module_context.unload_module_coroutine(self.module_name)
            self.module_object = None
            logging.info("unloaded module " + self.module_path)

    def unload(self):
        """Unload the currently loaded module"""
        self.get_context().thread_coroutine(self.unload_coroutine())

    def exception_handler(self, future):
        #Oops, something happened
        logging.error("Error in module run: " + self.module_path + ": " + str(future.exception()))

        #Try to load a replacement module.
        self.replace_faulty()

    @asyncio.coroutine
    def replace_faulty_coroutine(self):
        """Replace a faulty module with the next in line, aka increment fallback_index and trigger load()"""
        self.fallback_index += 1
        try:
            yield from self.load_coroutine()
        except Exception as e:
            logging.error("Error replacing faulty module: " + str(e))

    def replace_faulty(self):
        """Replace a faulty module with the next in line, aka increment fallback_index and trigger load()"""
        if self.module_context is None:
            raise ValueError("No context set.")
        self.module_context.thread_coroutine(self.replace_faulty_coroutine())