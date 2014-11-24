from multiprocessing import Process

class Module(object):
    module_process = None
    name = "module"

    def __init__(self):
        self.name = self.__class__.__name__

    def start(self):
        self.module_process = process.BaseProcess()

    def _run(self):
        pass


