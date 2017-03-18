
class OutdatedStateException(Exception):

    def __init__(self, module_id, key):
        super().__init__("module: {}, key: {}".format(module_id, key))
        self.module_id = module_id
        self.key = key


class UnreachableModuleException(Exception):

    def __init__(self, module_id):
        super().__init__("{}".format(module_id))
        self.module_id = module_id


class UnreachableMonitorException(Exception):

    def __init__(self, monitor_id):
        super().__init__("{}".format(monitor_id))
        self.monitor_id = monitor_id