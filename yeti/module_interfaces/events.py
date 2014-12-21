from functools import partial
from asyncio import Event

from ..context import get_context


context_datastore_key = "events"


def get_event(eid, context=None):
    if context is None:
        context = get_context()
    evdata, lock = context.get_interface_data(context_datastore_key)
    with lock:
        if eid not in evdata:
            evdata[eid] = Event(loop=context.get_event_loop())
        return evdata[eid]


def trigger_event_threadsafe(eid, context=None):
    if context is None:
        context = get_context()
    context.get_event_loop().call_soon_threadsafe(partial(trigger_event, eid, context))


def trigger_event(eid, context=None):
    if context is None:
        context = get_context()
    evdata, lock = context.get_interface_data(context_datastore_key)
    with lock:
        if eid not in evdata:
            evdata[eid] = Event()
        evdata[eid].set()


def clear_event_threadsafe(eid, context=None):
    if context is None:
        context = get_context()
    context.get_event_loop().call_soon_threadsafe(partial(clear_event, eid, context))


def clear_event(eid, context=None):
    if context is None:
        context = get_context()
    evdata, lock = context.get_interface_data(context_datastore_key)
    with lock:
        if eid not in evdata:
            evdata[eid] = Event()
        evdata[eid].clear()
