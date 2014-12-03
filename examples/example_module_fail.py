import yeti
import asyncio

class Example(yeti.Module):

    def module_init(self):
        self.add_task(self.say_hi())

    @asyncio.coroutine
    def say_hi(self):
        print("Hi")
        raise ValueError("Oops, this is a CRITICAL Error!")


def get_module():
    return Example
