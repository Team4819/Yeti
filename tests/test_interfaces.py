import pytest

@pytest.fixture
def module_interfaces():
    from yeti import interfaces
    return interfaces

def test_events(yeti, module_interfaces, context):
    yeti.set_context(context)
    assert not module_interfaces.events.get_event("uno").is_set()
    assert not module_interfaces.events.get_event("duo").is_set()
    module_interfaces.events.set_event("uno")
    assert module_interfaces.events.get_event("uno").is_set()
    assert not module_interfaces.events.get_event("duo").is_set()
    module_interfaces.events.clear_event("uno")
    assert not module_interfaces.events.get_event("uno").is_set()
    assert not module_interfaces.events.get_event("duo").is_set()

def test_datastreams(yeti, module_interfaces, context):
    yeti.set_context(context)
    stream1 = module_interfaces.datastreams.get_datastream("uno")
    stream2 = module_interfaces.datastreams.get_datastream("duo")
    assert stream1.get() == dict()
    assert stream2.get() == dict()
    stream1.push({"message": "Hello!"})
    stream2.push({"number": 5})
    assert module_interfaces.datastreams.get_datastream("uno").get()["message"] == "Hello!"
    assert module_interfaces.datastreams.get_datastream("duo").get()["number"] == 5

def test_datastream_events(yeti, module_interfaces, context):
    yeti.set_context(context)
    ds = module_interfaces.datastreams.get_datastream("uno")
    assert ds.get() == dict()
    ev = ds.set_event(lambda d: d.get("message", "") == "Hi there!")
    assert not ev.is_set()
    ds.push({"message": "Scram!"})
    assert not ev.is_set()
    ds.push({"message": "Hi there!"})
    assert ev.is_set()