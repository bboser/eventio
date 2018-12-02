import eventio

print(dir(eventio))

start_event = eventio.Event()

async def countdown(n):
    while n > 0:
        print('T-minus', n)
        await eventio.sleep(0.5)
        n -= 1

async def friend(name):
    print('Hi, my name is', name)
    print('Playing Minecraft')
    try:
        await eventio.sleep(10)
        print(name, "done playing")
    except eventio.CancelledError:
        print(name, 'going home')
        raise

async def kid():
    print('Can I play?')
    await start_event.wait()

    print('Building the Millenium Falcon in Minecraft')

    paul = await eventio.spawn(friend('Paul'))
    anna = await eventio.spawn(friend('Anna'))
    tom  = await eventio.spawn(friend('Tom'))
    try:
        await eventio.sleep(10)
    except eventio.CancelledError:
        await paul.cancel()
        await anna.cancel()
        await tom.cancel()
        print('Fine. Saving my work.')
        raise

async def parent():
    kid_task = await eventio.spawn(kid())
    await eventio.sleep(1)

    print('Yes, go play')
    await start_event.set()
    await eventio.sleep(4)

    print("Let's go")
    count_task = await eventio.spawn(countdown(4))
    print("count_task.join")
    await count_task.join()
    print("count_task joined")

    print("We're leaving!")
    print('I warned you!')
    print("cancel kid:", await kid_task.cancel())
    print('Leaving!')

eventio.run(parent())
