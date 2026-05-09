import ssl


class TLSManager:

    @staticmethod
    def create_ssl_context():

        ssl_context = ssl.create_default_context(
            ssl.Purpose.CLIENT_AUTH
        )

        ssl_context.load_cert_chain(
            certfile="certs/server.crt",
            keyfile="certs/server.key"
        )

        return ssl_context