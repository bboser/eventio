import digitalio
from .kernel import _get_kernel
from .traps import _scheduler_wait, _scheduler_wake

class Event:

    def __init__(self):
        self._set = False
        self._waitq = None

    def is_set(self):
        return self._set

    def clear(self):
        self._set = False

    async def wait(self):
        if self._set: return
        if not self._waitq:
            self._waitq = []
        await _scheduler_wait(self._waitq)

    async def set(self):
        self._set = True
        await _scheduler_wake(self._waitq)


class PinEvent(Event):

    def __init__(self, pin, pull=None):
        super().__init__()
        self.pin = digitalio.DigitalInOut(pin)
        self.pin.switch_to_input(pull=pull)
        self.pin.irq(handler=self._cb)

    def _cb(self, v):
        # interrupt callback, knows nothing about kernel
        if self._waitq:
            _get_kernel()._schedule(self._waitq)