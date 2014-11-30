import logging
import os
import imp
import traceback

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

    def replace_faulty(self):
        """Replace a faulty module with the next in line, aka increment fallback_index and trigger load()"""
        self.fallback_index += 1
        self.load()

    def reload(self):
        self.load()

    def add_fallback(self, fallback):
        self.fallback_list.append(fallback)

    def load(self, module_path=None):
        """
        Load a module into the wrapper, either from a name, or use the existing fallback_list and fallback_index
        """

        #Start by unloading any previously loaded module
        if self.module_object is None:
            self.unload()

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

                #Initialize the actual module object
                self.module_object = self.module_import.get_module()()

                #Get the module's name and file name
                self.module_name = self.module_object.name
                self.module_path = file_to_load

                #Yay, we must have been successful!
                break

            except Exception as e:
                #Oops, something happened. We must try the next one on the fallback list!
                logging.error("Error loading module: " + file_to_load + ": " + str(e) + "\n" + traceback.format_exc())
                self.fallback_index += 1

    def start(self):
        self.module_object._run_target = self.run
        self.module_object.start()

    def run(self):
        while True:
            try:
                self.module_object._run_loop()
                break

            except Exception as e:
                #Oops, something happened.
                logging.error("Error in module run: " + self.module_path + ": " + str(e) + "\n" + traceback.format_exc())

                #Try to load a replacement module.
                self.replace_faulty()

    def unload(self):
        """Unload the currently loaded module"""
        self.module_object = None
        logging.info("unloaded module " + self.module_name)

    def __getattr__(self, item):
        #Prevent a feedback loop
        if item == "module_object":
            raise AttributeError(item)
        #Get that attribute!
        return getattr(self.module_object, item)