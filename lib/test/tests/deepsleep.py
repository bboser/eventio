from microcontroller import deepsleep
from timer import Chronometer

def test_deepsleep():
    c = Chronometer()
    dt1 = 0.3
    dt2 = deepsleep(dt1)
    dt3 = c.elapsed_time
    assert dt3 <= dt1, "sleep no longer than timeout"
    assert dt3 == 0 or abs(dt2-dt3)/dt3 < 0.01, "report correct sleep time"