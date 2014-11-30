from .module import RunCondition
from threading import RLock

events = dict()
events_lock = RLock()


class EventCondition(RunCondition):
    eid = ""
    poll = 0

    def __init__(self, eid, poll=.2):
        self.eid = eid
        self.poll = poll
        with events_lock:
            if eid not in events:
                events[eid] = False

    def is_met(self, current_time):
        return events[self.eid], current_time + self.poll


class RisingEventCondition(RunCondition):
    eid = ""
    last_state = True
    poll = 0

    def __init__(self, eid, poll=.2):
        self.eid = eid
        self.poll = poll
        if eid not in events:
            events[eid] = False

    def is_met(self, current_time):
        with events_lock:
            met = events[self.eid] and not self.last_state
            self.last_state = events[self.eid]
            return met, current_time + self.poll


class FallingEventCondition(RunCondition):
    eid = ""
    last_state = False
    poll = 0

    def __init__(self, eid, poll=.2):
        self.eid = eid
        self.poll = poll
        if eid not in events:
            events[eid] = False

    def is_met(self, current_time):
        with events_lock:
            met = not events[self.eid] and self.last_state
            self.last_state = events[self.eid]
            return met, current_time + self.poll


def start_event(eid):
    with events_lock:
        events[eid] = True


def stop_event(eid):
    with events_lock:
        events[eid] = False