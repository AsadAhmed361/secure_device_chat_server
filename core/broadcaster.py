import json
import time


class Broadcaster:

    def __init__(self, room_manager):

        self.room_manager = room_manager

    async def broadcast(
        self,
        room,
        sender,
        data
    ):

        payload = {
            "type": "message",
            "room": room,
            "from": sender.device_id,
            "timestamp": int(time.time()),
            "data": data
        }

        encoded = (
            json.dumps(payload) + "\n"
        ).encode()

        for client in self.room_manager.get_clients(room):

            if client == sender:
                continue

            await client.send(encoded)