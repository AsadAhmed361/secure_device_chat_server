import json


class MessageParser:

    @staticmethod
    def parse(raw):

        return json.loads(raw.decode())