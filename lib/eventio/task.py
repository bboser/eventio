from .common import CancelledError, type_corof, type_coro, status_msg
from .common import status_active, status_terminated, status_cancel_pending, status_cancelled

class Task:

    def __init__(self, corofunc, *attr, **kwargs):
        self._status = status_active
        self.next_arg = None    # arg or exception for next iteration
        self.joining = None     # None, Task, or list of Task's waiting to join
        if isinstance(corofunc, type_corof):
            self.coro = corofunc(*attr, **kwargs)
        elif isinstance(corofunc, type_coro):
            self.coro = corofunc
        else:
            raise TypeError("Expected coroutine, got %s" % corofunc)

    async def join(self):
        def trap(kernel):
            if self._status == status_terminated:
                # task already terminated
                kernel.cur_task = self.next_arg
                kernel.readyq.put(kernel.cur_task)
            else:
                # wait for task to terminate, then reschedule caller (cur_task)
                self._add_joining(kernel.cur_task)
        return (yield trap)

    async def cancel(self, blocking=True):
        def trap(kernel):
            if self._status == status_terminated:
                # task already terminated
                kernel.cur_task.next_arg = False
                kernel.readyq.put(kernel.cur_task)
            else:
                # schedule task for cancellation
                self._status == status_cancel_pending
                self.next_arg = CancelledError()
                kernel.readyq.put(self)
                # reschedule caller
                kernel.cur_task.next_arg = True
                if blocking:
                    # wait for StopIteration
                    self._add_joining(kernel.cur_task)
                else:
                    # reschedule right away without waiting for cancellation
                    kernel.readyq.put(kernel.cur_task)
        return (yield trap)

    def _add_joining(self, task):
        if self.joining == None:
            self.joining = task
        elif isinstance(self.joining, type(self)):
            self.joining = [ self.joining, task ]
        else:
            self.joining.append(task)

    def _cancelled(self, kernel):
        # process joining, do not modify next_arg
        self._status = status_cancelled
        joining = self.joining
        if joining:
            if isinstance(joining, Task):
                kernel.readyq.put(joining)
                joining = None
            else:
                for t in joining:
                    kernel.readyq.put(t)
                joining.clear()
        # let the cancelled task terminate? why?
        # readyq.put(cur_task)


    def _terminated(self, kernel, result):
        # process joining, set next_arg to result
        self._status = status_terminated
        joining = self.joining
        if not joining: return
        if isinstance(joining, Task):
            joining.next_arg = result
            kernel.readyq.put(joining)
            joining = None
        else:
            for t in joining:
                t.next_arg = result
                kernel.readyq.put(t)
            joining.clear()

    @property
    def result(self):
        if self._status != status_terminated:
            raise RuntimeError('Task not terminated')
        return self.next_arg

    @property
    def status(self):
        return status_msg[self._status]

    @property
    def terminated(self):
        return self._status == status_terminated

    @property
    def name(self):
        return str(self.coro).split("'")[1]

    def __repr__(self):
        return "Task {}, arg={}, status={}".format(self.name, self.next_arg, self.status)

    def __str__(self):
        return self.__repr__()