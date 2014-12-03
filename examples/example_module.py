import yeti
import asyncio


class Example(yeti.Module):

    def module_init(self):
        self.add_task(self.say_hi("Hello world!"))

    @asyncio.coroutine
    def say_hi(self, message):
        while True:
            print(message)
            yield from asyncio.sleep(1)


def get_module():
    return Example

