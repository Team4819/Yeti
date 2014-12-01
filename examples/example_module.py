import yeti
import asyncio


class Example(yeti.AsyncioModule):

    def module_init(self):
        self.add_task(self.say_hi("Hello world!"))

    @asyncio.coroutine
    def say_hi(self, message):
        event = yeti.get_event("tick")
        print("tick")
        yield from event.wait()
        while True:
            print(message)
            yield from asyncio.sleep(1)


def get_module():
    return Example

