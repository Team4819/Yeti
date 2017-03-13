
class OutdatedStateException(Exception):

    def __init__(self, module_id, key):
        super().__init__("module: {}, key: {}".format(module_id, key))
        self.module_id = module_id
        self.key = key


class NoSuchModuleException(Exception):

    def __init__(self, module_id):
        super().__init__("{}".format(module_id))
        self.module_id = module_id
