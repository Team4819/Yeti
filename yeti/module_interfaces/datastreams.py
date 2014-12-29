from ..context import get_context
from functools import partial
import asyncio
import copy

context_datastore_key = "datastreams"


def get_datastream(dsid, context=None):
    if context is None:
        context = get_context()
    datastreams_data = context.get_interface_data(context_datastore_key)[0]
    if dsid not in datastreams_data:
        datastreams_data[dsid] = Datastream()
    return datastreams_data[dsid]


class Datastream(object):
    """
    Provides an interface to share data, in the form of a dictionary, between
    different modules, with mechanisms for thread-safe operation, and for
    triggering asyncio events when certain conditions are met.
    """

    def __init__(self):
        self.event_triggers = list()
        self.data = dict()

    def push(self, data):
        """
        :param data: The dictionary of data to :meth:`dict.update()` the existing
         dictionary with.
        """
        self.data.update(data)
        self._check_events()

    def push_threadsafe(self, data, context=None):
        """
        Schedules :meth:`.set` to be run in the current context's event loop.
        This method is thread-safe.

        :param data: The dictionary of data to give to :meth:`.set`
        :param context: The (optional) context to use for scheduling. Otherwise
            the current thread's context will be used.
        """
        if context is None:
            context = get_context()
        context.get_event_loop().call_soon_threadsafe(partial(self.push, data))

    def get(self):
        """
        :returns A copy of the contained data.
        """
        return self.data.copy()

    def _check_events(self):
        """Loops through all events, setting and clearing appropriately."""
        for event in self.event_triggers:
            if event["conditional"](self.data):
                event["event"].set()
            else:
                event["event"].clear()

    def set_event(self, conditional, event=None):
        """
        Adds a conditional to be evaluated at each :meth:`set()`. The event will be triggered
        when the conditional returns true, and cleared when the conditional returns false.

        :param conditional: A reference to a callable that accepts one argument,
            which is the current data dictionary held in the datastream.
        :param event: The optional event object to use. If none is provided, a new
            asyncio event will be created.

        :returns The event that will be triggered when the conditional returns True.
        """
        if event is None:
            event = asyncio.Event()
        self.event_triggers.append({"event": event, "conditional": conditional})

        #Update events.
        self._check_events()
        return event

    def drop_event(self, event):
        """
        Remove event and it's attached conditional from being triggered.

        :param event: The event object to remove.

        :returns True if successful.
        """
        for trigger in self.event_triggers[:]:
            if event is trigger["event"]:
                self.event_triggers.remove(event)
                return True
        return False