import asyncio

from device_client import DeviceClient


HOST = "127.0.0.1"
PORT = 9000

TOKEN = "device_token_2"

ROOM = "factory"


async def main():

    client = DeviceClient(
        HOST,
        PORT,
        TOKEN
    )

    await client.connect()

    await client.subscribe(ROOM)

    print("Listening...")

    while True:

        msg = await client.receive()

        if msg is None:
            break

        print("[MESSAGE]", msg)


asyncio.run(main())