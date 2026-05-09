import asyncio
import ssl
import json


class DeviceClient:

    def __init__(
        self,
        host,
        port,
        token
    ):

        self.host = host
        self.port = port
        self.token = token

        self.reader = None
        self.writer = None

    # ==========================================
    # SSL
    # ==========================================

    def create_ssl(self):

        ssl_ctx = ssl.create_default_context()

        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        return ssl_ctx

    # ==========================================
    # CONNECT
    # ==========================================

    async def connect(self):

        self.reader, self.writer = (
            await asyncio.open_connection(
                self.host,
                self.port,
                ssl=self.create_ssl()
            )
        )

        connect_msg = {
            "type": "connect",
            "token": self.token
        }

        await self.send_raw(connect_msg)

        print("[CONNECTED]")

    # ==========================================
    # SUBSCRIBE / JOIN ROOM
    # ==========================================

    async def subscribe(self, room):

        msg = {
            "type": "join",
            "room": room
        }

        await self.send_raw(msg)

        print(f"[SUBSCRIBED] {room}")

    # ==========================================
    # PUBLISH
    # ==========================================

    async def publish(
        self,
        room,
        data
    ):

        msg = {
            "type": "message",
            "room": room,
            "data": data
        }

        await self.send_raw(msg)

    # ==========================================
    # RECEIVE
    # ==========================================

    async def receive(self):

        data = await self.reader.readline()

        if not data:
            return None

        return json.loads(data.decode())

    # ==========================================
    # RAW SEND
    # ==========================================

    async def send_raw(self, payload):

        self.writer.write(
            (json.dumps(payload) + "\n").encode()
        )

        await self.writer.drain()

    # ==========================================
    # CLOSE
    # ==========================================

    async def close(self):

        self.writer.close()

        await self.writer.wait_closed()

        print("[DISCONNECTED]")