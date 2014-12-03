import asyncio

class Module(object):
    name = "module"
    context = None

    def __init__(self):
        self.name = self.__class__.__name__
        self.tasks = list()

    def bind_context(self, context):
        if self.context is not None:
            raise ValueError("Module already bound to context, cannot bind to another.")
        self.context = context

    def _init(self):
        self.module_init()

    def _deinit(self):
        for task in self.tasks:
            task.cancel()
        self.module_deinit()

    def module_init(self):
        pass

    def module_deinit(self):
        pass

    def add_task(self, function):
        if self.context is None:
            raise ValueError("No currently bound context")
        task = asyncio.async(function)
        self.tasks.append(task)

    def is_own_task(self, handle):
        return handle in self.tasks
