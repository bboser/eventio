from timer import Chronometer, Timer
from time import sleep

def test_chronometer():
    c = Chronometer()
    dt1 = 0.1
    sleep(dt1)
    assert c.elapsed_time >= dt1, "elapsed time"
    c.stop()
    dt2 = c.elapsed_time
    sleep(0.2)
    assert c.elapsed_time == dt2, "stopped time"
    c.resume()
    sleep(dt1)
    assert c.elapsed_time >= dt1+dt2, "elapsed time after resume"
    c.reset()
    assert c.elapsed_time == 0, "reset"


_c = Chronometer()
_i1 = 0.2

def _cb(timer):
    global _c, _i1
    assert _c.elapsed_time >= _i1, "Timer elapse"
    
def test_timer():
    global _c, _i1
    t = Timer(interval=_i1, function=_cb)
    _c.reset()
    t.start()
    sleep(_i1)
    