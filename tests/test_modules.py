import asyncio


def test_module_start(yeti):
    class TestMod(yeti.Module):
        pass
    context = yeti.Context()
    module = TestMod()
    context.add_module(module)
    context.run_for(.5)


def test_module_run(yeti):
    class SetterMod(yeti.Module):
        message = "..."

        def module_init(self):
            self.message = "Hi!"
    context = yeti.Context()
    module = SetterMod()
    context.add_module(module)
    assert module.message == "..."
    context.run_for(.5)
    assert module.message == "Hi!"


def test_module_task(yeti):
    class SetterMod(yeti.Module):
        message = "..."

        def module_init(self):
            self.add_task(self.set_message())

        @asyncio.coroutine
        def set_message(self):
            self.message = "Hi!"
    context = yeti.Context()
    module = SetterMod()
    context.add_module(module)
    assert module.message == "..."
    context.run_for(.5)
    assert module.message == "Hi!"