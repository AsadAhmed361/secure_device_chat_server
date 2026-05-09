class AuthManager:

    def __init__(self):

        self.tokens = {
            "device_token_1": {
                "device_id": "sensor_1",
                "rooms": [
                    "factory",
                    "alerts"
                ]
            },

            "device_token_2": {
                "device_id": "sensor_2",
                "rooms": [
                    "factory"
                ]
            },
            "device_token_3": {
                "device_id": "sensor_3",
                "rooms": [
                    "usaid"
                ]
            },
            "device_token_4": {
                "device_id": "sensor_4",
                "rooms": [
                    "usaid"
                ]
            }
        }

    def authenticate(self, token):

        return self.tokens.get(token)