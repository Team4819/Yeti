import asyncio

import yeti


class Example(yeti.Module):

    def module_init(self):
        self.add_task(self.say_hi())

    @asyncio.coroutine
    def say_hi(self):
        print("Hi")
        raise Exception("Oops, this is a CRITICAL Error!")

