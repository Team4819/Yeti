from ..context import get_context
from functools import partial
import asyncio
import copy

context_datastore_key = "datastreams"


def get_datastream(dsid):
    context = get_context()
    datastreams_data = context.get_interface_data(context_datastore_key)[0]
    if dsid not in datastreams_data:
        datastreams_data[dsid] = Datastream()
    return datastreams_data[dsid]


class Datastream(object):

    value = None

    def __init__(self):
        self.event_triggers = list()

    def set(self, value):
        self.value = copy.copy(value)
        for event_trigger in self.event_triggers:
            if event_trigger["conditional"](self.value):
                event_trigger["event"].set()

    def set_threadsafe(self, value, context=None):
        if context is None:
            context = get_context()
        context.get_event_loop().call_soon_threadsafe(partial(self.set, value))

    def get(self, default=None):
        if self.value is None:
            return default
        return copy.copy(self.value)

    def add_event_trigger(self, conditional):
        event = asyncio.Event()
        self.event_triggers.append({"event": event, "conditional": conditional})
        return event