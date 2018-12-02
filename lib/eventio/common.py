from micropython import const

# Task status codes

status_active          = const(1)
status_cancel_pending  = const(2)
status_timeout_pending = const(3)
status_cancelled       = const(4)
status_terminated      = const(5)

status_msg = [
    '',
    'active',
    'cancellation pending',
    'timeout pending',
    'cancelled',
    'terminated',
]

# Errors

class CancelledError(Exception): pass
class TimeoutError(Exception): pass

# Types

type_coro  = type((lambda: (yield))())  # Generator type
type_corof = type((lambda: (yield)))    # Generator function

# @coroutine decorator
def coroutine(func):
    return func
