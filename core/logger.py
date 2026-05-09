import logging


class Logger:

    @staticmethod
    def setup():

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s"
        )

        return logging.getLogger("SecureChatServer")