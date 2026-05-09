import asyncio
import json

from config.settings import Settings

from core.client import Client
from core.auth_manager import AuthManager
from core.room_manager import RoomManager
from core.broadcaster import Broadcaster
from core.rate_limiter import RateLimiter
from core.logger import Logger

from protocol.parser import MessageParser
from protocol.validator import MessageValidator

from security.tls import TLSManager


class SecureChatServer:

    def __init__(self):

        self.logger = Logger.setup()

        self.auth_manager = AuthManager()

        self.room_manager = RoomManager()

        self.broadcaster = Broadcaster(
            self.room_manager
        )

        self.clients = set()

    async def handle_client(
        self,
        reader,
        writer
    ):

        client = Client(
            reader,
            writer,
            Settings.QUEUE_SIZE
        )

        limiter = RateLimiter(
            Settings.RATE_LIMIT_MESSAGES,
            Settings.RATE_LIMIT_WINDOW
        )

        self.clients.add(client)

        addr = writer.get_extra_info("peername")

        self.logger.info(f"Connected: {addr}")

        try:

            while True:

                raw = await reader.readline()

                if not raw:
                    break

                if len(raw) > Settings.MAX_MESSAGE_SIZE:
                    break

                if not limiter.allow():
                    break

                try:
                    msg = MessageParser.parse(raw)
                except:
                    break

                if not MessageValidator.validate(msg):
                    break

                msg_type = msg.get("type")

                # =====================================
                # CONNECT
                # =====================================

                if msg_type == "connect":

                    token = msg.get("token")

                    auth = self.auth_manager.authenticate(token)

                    if not auth:
                        break

                    client.authenticated = True

                    client.device_id = auth["device_id"]

                    client.allowed_rooms = auth["rooms"]

                    response = {
                        "type": "connected",
                        "device_id": client.device_id
                    }

                    await client.send(
                        (
                            json.dumps(response) + "\n"
                        ).encode()
                    )

                # =====================================
                # REQUIRE AUTH
                # =====================================

                elif not client.authenticated:
                    break

                # =====================================
                # JOIN
                # =====================================

                elif msg_type == "join":

                    room = msg.get("room")

                    if room not in client.allowed_rooms:
                        continue

                    self.room_manager.join(
                        room,
                        client
                    )

                # =====================================
                # MESSAGE
                # =====================================

                elif msg_type == "message":

                    room = msg.get("room")

                    data = msg.get("data")

                    if room not in client.joined_rooms:
                        continue

                    asyncio.create_task(
                        self.broadcaster.broadcast(
                            room,
                            client,
                            data
                        )
                    )

        except Exception as e:

            self.logger.error(str(e))

        finally:

            for room in client.joined_rooms:
                self.room_manager.leave(room, client)

            self.clients.discard(client)

            await client.close()

            self.logger.info("Client disconnected")

    async def start(self):

        ssl_context = TLSManager.create_ssl_context()

        server = await asyncio.start_server(
            self.handle_client,
            Settings.HOST,
            Settings.PORT,
            ssl=ssl_context,
            limit=Settings.MAX_MESSAGE_SIZE
        )

        self.logger.info(
            f"Server running on "
            f"{Settings.HOST}:{Settings.PORT}"
        )

        async with server:
            await server.serve_forever()