from collections import defaultdict


class RoomManager:

    def __init__(self):

        self.rooms = defaultdict(set)

    def join(self, room, client):

        self.rooms[room].add(client)

        client.joined_rooms.add(room)

    def leave(self, room, client):

        self.rooms[room].discard(client)

    def get_clients(self, room):

        return self.rooms.get(room, set())