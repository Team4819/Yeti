import asyncio

def test_module_run(yeti):
    class SetterMod(yeti.Module):
        message = "..."

        def module_init(self):
            self.message = "Hi!"
            self.event_loop.stop()

    module = SetterMod()
    event_loop = asyncio.get_event_loop()
    assert module.message == "..."
    module.start(loop=event_loop)
    event_loop.run_forever()
    assert module.message == "Hi!"


def test_module_task(yeti):
    class SetterMod(yeti.Module):
        message = "..."

        def module_init(self):
            self.add_task(self.set_message())

        @asyncio.coroutine
        def set_message(self):
            self.message = "Hi!"
            self.event_loop.stop()

    module = SetterMod()
    event_loop = asyncio.get_event_loop()
    assert module.message == "..."
    module.start(loop=event_loop)
    event_loop.run_forever()
    assert module.message == "Hi!"