import utime
import _iot
from microcontroller import deepsleep
from timer import Chronometer

from .common import status_terminated
from .common import CancelledError
from .task import Task


class Kernel:
    # do we even need a class? for time_actual?

    def __init__(self, readyq_len=16, waitq_len=16):
        self.cur_task = None
        self.readyq = _iot.AtomicFIFO(readyq_len) # interrupt safe queue of coro or (coro, arg)
        self.waitq  = _iot.waitq(waitq_len)       # queue ordered by time
        self.time_actual = Chronometer()          # kernel uptime
        self.time_working = Chronometer()         # kernel awake (not deepsleep)

    def uptime(self):
        """Kernel uptime in seconds"""
        return self.time_actual.elapsed_time

    def load_average(self):
        """Load average in percent.
        100% means CPU was always active, 0% means deepsleep (power down) all the time."""
        total = self.time_actual.elapsed_time
        wake  = self.time_working.elapsed_time
        return 100 * wake / total

    # ok to call from interrupt handler (e.g. PinEvent)
    def _schedule(self, queue):
        if queue:
            [ self.readyq.put(t) for t in queue ]
            queue.clear()

    # run until no more ready or waiting tasks
    def _run(self, task):
        """Run task.
        Call only once, not from kernel. Use `spawn` to create additional tasks.
        Returns after all tasks have finished.
        """
        readyq = self.readyq
        waitq  = self.waitq

        readyq.put(task)

        # run until there is nothing left to do
        while True:
            # schedule tasks from the waitq that are ready to run
            tnow = utime.ticks_ms()
            while bool(waitq):
                dt = utime.ticks_diff(waitq.peektime(), tnow)
                if dt > 0:
                    # not ready yet
                    break
                # schedule for execution
                task = waitq.pop()
                # print("wake up", waiting_task[1])
                if task._status != status_terminated:
                    readyq.put(task)

            if bool(readyq):
                for i in range(len(readyq)):
                    self._run_task()
            else:
                # readyq is empty
                if bool(waitq):
                    # TODO: check if all tasks on waitq are stopped/cancelled
                    # deepsleep until waitq needs attention
                    ds = max(0, utime.ticks_diff(self.waitq.peektime(), tnow))
                    if ds > 1:
                        # leisure time
                        # run gc?
                        if ds > 5:
                            # ######## TODO ###############################################
                            # check if all tasks in waitq are cancelled?
                            pass
                    self.time_working.stop()
                    deepsleep(ds/1000.0)
                    self.time_working.resume()
                else:
                    # print("queues are empty --> quit kernel")
                    return

    # run task once
    def _run_task(self):
        readyq = self.readyq
        self.cur_task = cur_task = readyq.get()
        if cur_task._status == status_terminated:
            return
        next_arg = cur_task.next_arg
        cur_task.next_arg = None
        try:
            if isinstance(next_arg, Exception):
                # print("throw {} to {}".format(type(next_arg), cur_task))
                trap = cur_task.coro.throw(next_arg)
            else:
                # print("send  {} to {}".format(next_arg, cur_task))
                trap = cur_task.coro.send(next_arg)
        except CancelledError:
            cur_task._cancelled(self)
        except StopIteration as e:
            cur_task._terminated(self, e.value)
        except Exception as error:
            # prevent errors in tasks from ending the loop
            print("Kernel caught", type(error), error)
            # what does curio do?
            cur_task.next_arg = error
            cur_task.status = status_terminated
        else:
            # service trap (sleep, cancel, join, ...)
            trap(self)


# global instance
_kernel = None

def _get_kernel():
    global _kernel
    if not _kernel: raise RuntimeError("kernel is not running, call eventio.run first")
    return _kernel

def run(corofunc, *args, readyq_len=16, waitq_len=16, **kwargs):
    global _kernel
    if _kernel: raise RuntimeError("kernel is already running, use eventio.spawn to launch tasks")
    try:
        _kernel = Kernel(readyq_len=16, waitq_len=16)
        _kernel._run(Task(corofunc, *args, **kwargs))
    except Exception as e:
        raise RuntimeError("eventio Kernel aborted with error", e)
    _kernel = None
