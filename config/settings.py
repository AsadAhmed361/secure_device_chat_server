import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 9000))

    MAX_MESSAGE_SIZE = int(
        os.getenv("MAX_MESSAGE_SIZE", 4096)
    )

    QUEUE_SIZE = int(
        os.getenv("QUEUE_SIZE", 200)
    )

    RATE_LIMIT_MESSAGES = int(
        os.getenv("RATE_LIMIT_MESSAGES", 10)
    )

    RATE_LIMIT_WINDOW = int(
        os.getenv("RATE_LIMIT_WINDOW", 5)
    )