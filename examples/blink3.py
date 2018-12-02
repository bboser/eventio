from timer import Chronometer
from board import LED_R, LED_G, LED_B, MODE
import eventio
import digitalio

chrono = Chronometer()

sw1_event = eventio.PinEvent(MODE, pull=digitalio.Pull.UP)

async def blink(color, pin, period):
    global chrono
    p = digitalio.DigitalInOut(pin)
    p.direction = digitalio.Direction.OUTPUT
    try:
        while True:
            await eventio.sleep(period/2)
            p.value = not p.value
            chrono.reset()
    except eventio.CancelledError:
        p.value = False   # LED off
        p.deinit()
        print(color, "cancelled")
        raise

async def main():
    r = await eventio.spawn(blink("red  ", LED_R, 0.7))
    g = await eventio.spawn(blink("green", LED_G, 0.3))
    b = await eventio.spawn(blink("blue ", LED_B, 0.5))
    print("All LEDs blinking ...")
    await sw1_event.wait()
    print("Button pressed! Cancelling blinkers ...")
    await r.cancel()
    await g.cancel()
    await b.cancel()
    # print some statistics, sleep needed because of bug: cancel overrides next_arg
    # await eventio.sleep(2)
    kernel = await eventio.get_kernel()
    print("Program ran for {} seconds with {} % CPU utilization".format(
        kernel.uptime(), kernel.load_average()
    ))

eventio.run(main)