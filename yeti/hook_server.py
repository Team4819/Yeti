import logging


class HookServer(object):

    def __init__(self):
        self.logger = logging.getLogger("yeti." + self.__class__.__name__)
        self.hooks = dict()

    def add_hook(self, hook_name, callback):
        if hook_name not in self.hooks:
            self.hooks[hook_name] = list()
        self.hooks[hook_name].append(callback)

    def call_hook(self, hook_name, *args, **kwargs):
        retval = False
        if hook_name in self.hooks:
            for hook in self.hooks[hook_name]:
                try:
                    hook(*args, **kwargs)
                    retval = True
                except Exception as e:
                    self.logger.exception("Exception on hook call: {}".format(e))
        return retval

