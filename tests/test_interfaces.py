def test_events(yeti, context):
    from yeti.interfaces import events
    yeti.set_context(context)
    assert not events.get_event("uno").is_set()
    assert not events.get_event("duo").is_set()
    events.set_event("uno")
    assert events.get_event("uno").is_set()
    assert not events.get_event("duo").is_set()
    events.clear_event("uno")
    assert not events.get_event("uno").is_set()
    assert not events.get_event("duo").is_set()

def test_datastreams(yeti, context):
    from yeti.interfaces import datastreams
    yeti.set_context(context)
    stream1 = datastreams.get_datastream("uno")
    stream2 = datastreams.get_datastream("duo")
    assert stream1.get() == dict()
    assert stream2.get() == dict()
    stream1.push({"message": "Hello!"})
    stream2.push({"number": 5})
    assert datastreams.get_datastream("uno").get()["message"] == "Hello!"
    assert datastreams.get_datastream("duo").get()["number"] == 5

def test_datastream_events(yeti, context):
    from yeti.interfaces import datastreams
    yeti.set_context(context)
    ds = datastreams.get_datastream("uno")
    assert ds.get() == dict()
    ev = ds.set_event(lambda d: d.get("message", "") == "Hi there!")
    assert not ev.is_set()
    ds.push({"message": "Scram!"})
    assert not ev.is_set()
    ds.push({"message": "Hi there!"})
    assert ev.is_set()

def test_remote_coroutines(yeti, context):
    from yeti.interfaces import remote_methods
    from yeti.module import Module
    from yeti import autorun_coroutine
    import asyncio

    class ModA(Module):
        def module_init(self):
            self.msg = ""

        @remote_methods.public_coroutine
        @asyncio.coroutine
        def setter(self, msg):
            self.msg = msg

    class ModB(Module):
        @autorun_coroutine
        @asyncio.coroutine
        def caller(self):
            yield from remote_methods.call_public_coroutine("setter", "Hi!")
            self.event_loop.stop()

    mymoda = ModA()
    mymodb = ModB()
    context.load_module(mymoda)
    context.load_module(mymodb)
    context.run_forever()
    assert mymoda.msg == "Hi!"

