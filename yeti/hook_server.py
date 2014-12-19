import logging


class Hook(object):
    """
    This provides an interface for a method used as a hook with a :class:HookServer
    """

    def __init__(self, hook_server, hook_name, func):
        """
        :param hook_server: The instance of :class:HookServer that uses this hook.
        :param hook_id: The
        :param func: The function to use with the hook.
        """
        self.func = func
        self.hook_server = hook_server
        self.hook_name = hook_name

    def call(self, *args, **kwargs):
        """
        Triggers all hooks registered with hook_server for hook_name
        """
        self.hook_server.call_hook(*args, **kwargs)

    def unset(self):
        """
        Removes the trigger from hook_server
        """
        self.hook_server.remove_hook(self)


class HookServer(object):
    """
    This provides a convenient hook registration mechanism.
    """

    def __init__(self):
        self.logger = logging.getLogger("yeti." + self.__class__.__name__)
        self._hooks = dict()

    def add_hook(self, hook_name, callback):
        """
        :param hook_name: The name of the function to create a hook for.
        :param callback: The method to use for the hook.
        Adds callback to the list of hooks to be run when hook_name is called.
        :returns The created instance of :class:Hook
        """
        hook = Hook(self, hook_name, callback)
        if hook_name not in self._hooks:
            self._hooks[hook_name] = list()
        self._hooks[hook_name].append(hook)
        return hook

    def call_hook(self, hook_name, *args, **kwargs):
        """
        :param hook_name: The name of hook to be called
        Calls all hooks that have been added to this :class:HookServer under the name hook_name with all extra
        provided parameters.
        :returns If at least one hook was successfully called.
        """
        retval = False
        if hook_name in self._hooks:
            for hook in self._hooks[hook_name]:
                try:
                    hook(*args, **kwargs)
                    retval = True
                except Exception as e:
                    self.logger.exception("Exception on hook call: {}".format(e))
        return retval

    def remove_hook(self, hook):
        """
        :param hook: The :class:Hook object to remove
        :returns Weather or not removal was successful.
        Removes hook from the instance of :class:HookServer
        """
        if hook in self._hooks[hook.hook_name]:
            self._hooks[hook.hook_name].remove(hook)
            return True
        return False

