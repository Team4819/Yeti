import logging

from .module_loader import ModuleLoader


class ConfigurationError(Exception):
    pass


class ConfigManager(object):

    STARTUP_MOD_SECTION = "StartupMods"

    def __init__(self):
        self.config_structure = None

    def load_startup_mods(self, context):
        if self.config_structure is None:
            raise ConfigurationError("No config file loaded.")
        for module_name in self.config_structure[self.STARTUP_MOD_SECTION]:
            self.load_module(module_name, context)

    def load_module(self, name, context):

        if self.config_structure is None:
            fallback_list = [name]

        #is it a subsystem name?
        elif name in self.config_structure:
            fallback_list = self.config_structure[name]

        #no? must be a filename then.
        else:
            #Search for filename in loaded config
            for subsystem_config in self.config_structure:
                if subsystem_config != self.STARTUP_MOD_SECTION and name in self.config_structure[subsystem_config]:
                    #We found it! set the fallback list
                    fallback_list = self.config_structure[subsystem_config]
                    break

            #If we still don't have a fallback list, just make one up and go!
            else:
                fallback_list = [name]

        module_loader = ModuleLoader()
        module_loader.set_context(context)
        module_loader.fallback_list = fallback_list
        module_loader.load()

    def parse_config_file(self, path):
        """Parse the module config file, returns a dictionary of all config file entries"""
        #Open the file
        f = open(path)
        section = None
        parsed_config = dict()

        #for each line in file:
        for line in f:
            #Get rid of extra spaces and carriage-returns
            line = line.rstrip('\r\n')

            #If there is a comment on the line, get rid of everything after the comment symbol and trim whitespace
            #Example: hi there #This is a comment
            if "#" in line:
                line, comment = line.split("#", 1)
                line = line.strip()

            #If there is a section header on the line, figure out what it's name is, and save it
            if "[" in line:
                #Example: [StartupMods]
                section = line.split("[", 1)[1].split("]", 1)[0]
                parsed_config[section] = list()

            #If there is no section header, than the line must contian data, so save it under the current section
            else:
                if line is not "":
                    parsed_config[section].append(line)

        #Message the system
        logging.info("Finished parsing " + path)
        self.config_structure = parsed_config
        return parsed_config
