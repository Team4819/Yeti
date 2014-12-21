import pytest

@pytest.fixture
def module_interfaces():
    from yeti import module_interfaces
    return module_interfaces

def test_events(yeti, module_interfaces, context):
    yeti.set_context(context)
    assert not module_interfaces.events.get_event("uno").is_set()
    assert not module_interfaces.events.get_event("duo").is_set()
    module_interfaces.events.trigger_event("uno")
    assert module_interfaces.events.get_event("uno").is_set()
    assert not module_interfaces.events.get_event("duo").is_set()
    module_interfaces.events.clear_event("uno")
    assert not module_interfaces.events.get_event("uno").is_set()
    assert not module_interfaces.events.get_event("duo").is_set()

def test_datastreams(yeti, module_interfaces, context):
    yeti.set_context(context)
    stream1 = module_interfaces.datastreams.get_datastream("uno")
    stream2 = module_interfaces.datastreams.get_datastream("duo")
    assert stream1.get(1) == 1
    assert stream1.get("hi there") == "hi there"
    stream1.set("Hello!")
    stream2.set(5)
    assert module_interfaces.datastreams.get_datastream("uno").get("1") == "Hello!"
    assert module_interfaces.datastreams.get_datastream("duo").get("1") == 5

def test_datastream_events(yeti, module_interfaces, context):
    yeti.set_context(context)
    ds = module_interfaces.datastreams.get_datastream("uno")
    assert ds.get(1) == 1
    ev = ds.add_event_trigger(lambda x: x == "Hi there!")
    assert not ev.is_set()
    ds.set("Hi there!")
    assert ev.is_set()