import asyncio
import random

from device_client import DeviceClient


HOST = "127.0.0.1"
PORT = 9000

TOKEN = "device_token_1"

ROOM = "factory"


async def main():

    client = DeviceClient(
        HOST,
        PORT,
        TOKEN
    )

    await client.connect()

    await client.subscribe(ROOM)

    while True:

        data = {
            "temperature": random.randint(20, 40)
        }

        await client.publish(
            ROOM,
            data
        )

        print("[PUBLISHED]", data)

        await asyncio.sleep(1)


asyncio.run(main())