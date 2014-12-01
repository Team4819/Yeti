from asyncio import Event
from threading import RLock

events = dict()
events_lock = RLock()


def get_event(eid):
    with events_lock:
        if eid not in events:
            events[eid] = Event()
            events[eid].clear()
        return events[eid]


def trigger_event(eid):
    with events_lock:
        event = get_event(eid)
        event.set()


def reset_event(eid):
    with events_lock:
        event = get_event(eid)
        event.clear()