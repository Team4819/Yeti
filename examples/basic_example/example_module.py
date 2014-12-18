import asyncio
import yeti
from yeti.module_interfaces import events

class Example(yeti.Module):

    def module_init(self):
        self.add_task(self.say_hi("Hello world!"))
        self.add_task(self.tactfull_hello())

    @asyncio.coroutine
    def tactfull_hello(self):
        yield from events.get_event("tick").wait()
        print("... hi?")

    @asyncio.coroutine
    def say_hi(self, message):
        while True:
            print(message)
            yield from asyncio.sleep(1)

