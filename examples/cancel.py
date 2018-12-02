import eventio

async def kid():
    print("Playing")
    try:
        await eventio.sleep(5)
        print("kid finished playing")
    except eventio.CancelledError:
        print("saving my work")
        raise
    print("done playing")

async def countdown(n):
    child = await eventio.spawn(kid())
    while n > 0:
        print('T-minus', n)
        await eventio.sleep(0.5)
        n -= 1
    print("cancel kid:", await child.cancel())
    kernel = await eventio.get_kernel()
    print("Took {} seconds, {} % CPU utilization".format(
        kernel.uptime(), kernel.load_average()
    ))

eventio.run(countdown, 3)
