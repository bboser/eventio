import utime
from .common import coroutine
from .task import Task

@coroutine
def get_kernel():
    """Reference to kernel"""
    def trap(kernel):
        kernel.cur_task.next_arg = kernel
        kernel.readyq.put(kernel.cur_task)
    return (yield trap)

@coroutine
def current_task():
    """Reference to the current task"""
    def trap(kernel):
        kernel.cur_task.next_arg = kernel.cur_task
        kernel.readyq.put(kernel.cur_task)
    return (yield trap)

@coroutine
def sleep(delay):
    """Suspend task for delay seconds"""
    # we work internally with 32-bit time in [ms]
    if delay > 1e6: raise ValueError("delay must be < 1e6")
    def trap(kernel):
        wakeup_time_ms = utime.ticks_add(utime.ticks_ms(), int(1000*delay))
        kernel.waitq.push(wakeup_time_ms, kernel.cur_task)
    yield trap

@coroutine
def spawn(child, *args, **kwargs):
    """Launch child task"""
    child_task = Task(child, *args, **kwargs)
    def trap(kernel):
        kernel.readyq.put(child_task)
        kernel.cur_task.next_arg = child_task
        kernel.readyq.put(kernel.cur_task)
    return (yield trap)

async def _cancel_after(task, seconds):
    await sleep(seconds)
    await task.cancel()

async def timeout_after(seconds, corofunc, *args, **kwargs):
    """Run corofunc and return its result or timeout"""
    long_task = await spawn(corofunc, *args, **kwargs)
    await spawn(_cancel_after, long_task, seconds)
    return await long_task.join()

@coroutine
def _scheduler_wait(waitq):
    def trap(kernel):
        # add task to signal's waitq
        waitq.append(kernel.cur_task)
    yield trap

@coroutine
def _scheduler_wake(waitq):
    def trap(kernel):
        # schedule all tasks on signal's waitq
        kernel._schedule(waitq)
        kernel.readyq.put(kernel.cur_task)
    yield trap