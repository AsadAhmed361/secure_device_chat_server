import asyncio


class Client:

    def __init__(
        self,
        reader,
        writer,
        queue_size
    ):

        self.reader = reader
        self.writer = writer

        self.authenticated = False

        self.device_id = None
        self.allowed_rooms = []
        self.joined_rooms = set()

        self.send_queue = asyncio.Queue(
            maxsize=queue_size
        )

        self.writer_task = asyncio.create_task(
            self.writer_loop()
        )

    async def writer_loop(self):

        try:
            while True:

                msg = await self.send_queue.get()

                self.writer.write(msg)

                await self.writer.drain()

        except:
            pass

    async def send(self, data: bytes):

        if self.send_queue.full():
            return

        await self.send_queue.put(data)

    async def close(self):

        self.writer_task.cancel()

        self.writer.close()

        await self.writer.wait_closed()