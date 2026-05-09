class MessageValidator:

    @staticmethod
    def validate(msg):

        if "type" not in msg:
            return False

        return True