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
    from yeti.interfaces import object_proxy
    from yeti.module import Module
    from yeti import autorun_coroutine
    import asyncio

    class ModA(Module):
        def module_init(self):
            self.msg = ""

        @object_proxy.public_object
        @asyncio.coroutine
        def alpha(self, msg):
            self.msg += msg

        @object_proxy.public_object(prefix="testmod")
        def beta(self, msg):
            self.msg += msg

        @object_proxy.public_object(name="setter_func")
        def gamma(self, msg):
            self.msg += msg

    class ModB(Module):
        @autorun_coroutine
        @asyncio.coroutine
        def caller(self):
            yield from object_proxy.call_public_coroutine("alpha", "Hi ")
            object_proxy.call_public_method("testmod.beta", "There")
            object_proxy.call_public_method("setter_func", "!")
            self.event_loop.stop()

    mymoda = ModA()
    mymodb = ModB()
    context.load_module_instance(mymoda)
    context.load_module_instance(mymodb)
    context.run_forever()
    assert mymoda.msg == "Hi There!"

