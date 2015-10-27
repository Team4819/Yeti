from yeti import Module
import asyncio


class Triggers(Module):

    def module_init(self):
        pass

    def on_rising_edge(self, value_poll, callback, poll_time=.2, repeat=True):
        coro =self.wait_for_rising_edge(value_poll,
                                        callback,
                                        poll_time=poll_time)
        if repeat:
            self.start_coroutine(self.repeat_coroutine(coro))
        else:
            self.start_coroutine(coro)

    def on_value(self, value_poll, value_target, value_tolerance=None, callback=None, poll_time=.2, repeat=True):
        coro = self.wait_for_value(value_poll,
                                   value_target,
                                   value_tolerance,
                                   callback,
                                   poll_time)
        if repeat:
            self.start_coroutine(self.repeat_coroutine(coro))
        else:
            self.start_coroutine(coro)

    def compare_value(self, value, target, tolerance=None):
        if tolerance is None:
            return value == target
        return abs(value - target) <= tolerance

    @asyncio.coroutine
    def repeat_coroutine(self, coroutine):
        while True:
            yield from coroutine
            yield from asyncio.sleep(.2)

    @asyncio.coroutine
    def wait_for_value(self, value_poll, value_target, value_tolerance=None, callback=None, poll_time=.2):
        yield from self.wait_for_condition(lambda: self.compare_value(value_poll(), value_target, value_tolerance),
                                           callback=callback,
                                           poll_time=poll_time)

    @asyncio.coroutine
    def wait_for_rising_edge(self, condition, callback=None, poll_time=.2):
        yield from self.wait_for_condition(lambda: not condition(), poll_time=poll_time)
        yield from self.wait_for_condition(condition, callback=callback, poll_time=poll_time)

    @asyncio.coroutine
    def wait_for_condition(self, condition, callback=None, poll_time=.2):
        while not condition():
            yield from asyncio.sleep(poll_time)
        if callback is None:
            return
        elif asyncio.iscoroutine(callback):
            yield from callback
        else:
            callback()