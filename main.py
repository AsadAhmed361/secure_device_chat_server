import asyncio

from core.server import SecureChatServer


async def main():

    server = SecureChatServer() 

    await server.start()


if __name__ == "__main__":

    asyncio.run(main())