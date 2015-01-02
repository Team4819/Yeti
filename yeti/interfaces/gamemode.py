"""
This is an interface designed to make it easier to communicate
gamemode between modules.
"""

from ..context import get_context
import asyncio

context_data_key = "gamemode"

DISABLED = 0
TELEOPERATED = 1
AUTONOMOUS = 2

def set_gamemode(mode, context=None):
    """
    Sets the current gamemode and releases any coroutines waiting for it.

    :param mode: The gamemode to set.
    :param context: The optional context to use for data storage. If none, the current
        thread’s context will be used.
    """
    if context is None:
        context = get_context()
    data, lock = context.get_interface_data(context_data_key)
    with lock:
        data["mode"] = mode
        context.thread_coroutine(_on_gamemode_set(mode, context))

def _on_gamemode_set(mode, context):
    """
    Sets all saved events for the given gamemode
    """
    data, lock = context.get_interface_data(context_data_key)
    events = data.get("events-mode-" + str(mode), None)
    if events is not None:
        for event in events:
            event.set()


@asyncio.coroutine
def wait_for_gamemode(modes, context=None):
    """
    Waits until one of the indicated modes is set.

    This is an asyncio coroutine.

    :param modes: One or more modes to wait for.
    :param context: The optional context to use for data storage. If none, the current
        thread’s context will be used.
    """

    if isinstance(modes, int):
        modes = [modes, ]

    if context is None:
        context = get_context()
    data, lock = context.get_interface_data(context_data_key)

    event = asyncio.Event()

    for mode in modes:
        if mode == data.get("mode", ""):
            return
        events_key = "events-mode-" + str(mode)
        if events_key not in data:
            data[events_key] = list()

        data[events_key].append(event)

    yield from event.wait()

    for mode in modes:
        events_key = "events-mode-" + str(mode)
        data[events_key].remove(event)

@asyncio.coroutine
def wait_for_disabled(context=None):
    """
    Waits until the disabled mode is set.

    This is an asyncio coroutine.

    :param context: The optional context to use for data storage. If none, the current
        thread’s context will be used.
    """
    yield from wait_for_gamemode(DISABLED, context=context)

@asyncio.coroutine
def wait_for_teleop(context=None):
    """
    Waits until the teleoperated mode is set.

    This is an asyncio coroutine.

    :param context: The optional context to use for data storage. If none, the current
        thread’s context will be used.
    """
    yield from wait_for_gamemode(TELEOPERATED, context=context)

@asyncio.coroutine
def wait_for_autonomous(context=None):
    """
    Waits until the autonomous mode is set.

    This is an asyncio coroutine.

    :param context: The optional context to use for data storage. If none, the current
        thread’s context will be used.
    """
    yield from wait_for_gamemode(AUTONOMOUS, context=context)

@asyncio.coroutine
def wait_for_enabled(context=None):
    """
    Waits until either the autonomous mode or the teleoperated mode is set.

    This is an asyncio coroutine.

    :param context: The optional context to use for data storage. If none, the current
        thread’s context will be used.
    """
    yield from wait_for_gamemode((TELEOPERATED, AUTONOMOUS), context=context)