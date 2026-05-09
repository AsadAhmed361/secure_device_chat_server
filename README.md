# Secure IoT Chat Server

A lightweight, real-time messaging server built for IoT device-to-device communication. Devices connect over TLS, authenticate with pre-shared tokens, join topic-based rooms, and exchange structured JSON messages with built-in rate limiting and async I/O.

---

## Features

- TLS-encrypted TCP connections on every client
- Token-based device authentication
- Room-based pub/sub messaging
- Sliding-window rate limiting per connection
- Async I/O with `asyncio` — handles many concurrent devices efficiently
- Bounded per-client send queues (slow clients never block the server)
- Clean disconnect and room cleanup on connection loss

---

## Project Structure

```
├── main.py                  # Entry point
├── config/
│   └── settings.py          # Environment-based configuration
├── core/
│   ├── server.py            # Main server logic and message routing
│   ├── client.py            # Connected device representation
│   ├── auth_manager.py      # Token authentication
│   ├── room_manager.py      # Room membership tracking
│   ├── broadcaster.py       # Fan-out message delivery
│   ├── rate_limiter.py      # Sliding-window rate limiter
│   └── logger.py            # Logging setup
├── protocol/
│   ├── parser.py            # JSON message parser
│   └── validator.py         # Message validator
├── security/
│   └── tls.py               # TLS/SSL context builder
├── certs/
│   ├── server.crt           # TLS certificate (not committed)
│   └── server.key           # TLS private key (not committed)
├── device_client.py         # Reusable Python client SDK
├── sender.py                # Example sender device
└── reciever.py              # Example receiver device
```

---

## Requirements

- Python 3.10+
- `python-dotenv`

```bash
pip install python-dotenv
```

---

## Setup

### 1. Generate TLS Certificates

```bash
mkdir -p certs

openssl req -x509 -newkey rsa:4096 \
    -keyout certs/server.key \
    -out certs/server.crt \
    -days 365 -nodes \
    -subj '/CN=localhost'
```

> For production, use a CA-signed certificate or create your own CA. See the [TLS section](#tls--security) below.

### 2. Configure Environment

Create a `.env` file in the project root:

```env
HOST=0.0.0.0
PORT=9000
MAX_MESSAGE_SIZE=4096
QUEUE_SIZE=200
RATE_LIMIT_MESSAGES=10
RATE_LIMIT_WINDOW=5
```

All values shown are the defaults. The `.env` file is optional — defaults apply if it is absent.

### 3. Run the Server

```bash
python main.py
```

---

## Message Protocol

All messages are **newline-delimited JSON** (`\n` terminated) over the TLS TCP connection.

### Client → Server

**Authenticate**
```json
{ "type": "connect", "token": "device_token_1" }
```

**Join a room**
```json
{ "type": "join", "room": "factory" }
```

**Publish a message**
```json
{ "type": "message", "room": "factory", "data": { "temperature": 34 } }
```

### Server → Client

**Authentication accepted**
```json
{ "type": "connected", "device_id": "sensor_1" }
```

**Incoming broadcast**
```json
{
  "type": "message",
  "room": "factory",
  "from": "sensor_1",
  "timestamp": 1715300000,
  "data": { "temperature": 34 }
}
```

---

## Connection Lifecycle

```
Client connects (TLS)
    └── sends connect + token
            └── server responds with connected
                    └── client sends join messages
                            └── client sends / receives messages
                                    └── client disconnects → server cleans up rooms
```

Any protocol violation (bad JSON, unknown token, missing `type`, rate limit exceeded) results in immediate disconnection.

---

## Authentication

Tokens are defined in `core/auth_manager.py`. Each token maps to a device ID and a list of permitted rooms:

```python
self.tokens = {
    "device_token_1": { "device_id": "sensor_1", "rooms": ["factory", "alerts"] },
    "device_token_2": { "device_id": "sensor_2", "rooms": ["factory"] },
    "device_token_3": { "device_id": "sensor_3", "rooms": ["usaid"] },
    "device_token_4": { "device_id": "sensor_4", "rooms": ["usaid"] },
}
```

> For production, replace the in-memory dictionary with a database or secrets manager and rotate tokens regularly.

---

## Rate Limiting

Each client gets its own sliding-window rate limiter. The defaults allow **10 messages per 5-second window**. Exceeding the limit disconnects the client immediately. Adjust via environment variables:

```env
RATE_LIMIT_MESSAGES=10
RATE_LIMIT_WINDOW=5
```

---

## Python Client SDK

`device_client.py` provides a high-level async client for any Python device:

```python
from device_client import DeviceClient

client = DeviceClient("127.0.0.1", 9000, "device_token_1")
await client.connect()
await client.subscribe("factory")

# Publish
await client.publish("factory", {"temperature": 34})

# Receive
msg = await client.receive()   # returns a dict

await client.close()
```

### Run the Example Sender

```bash
python sender.py
```

Publishes a random temperature reading to the `factory` room every second using `device_token_1`.

### Run the Example Receiver

```bash
python reciever.py
```

Listens on the `factory` room using `device_token_2` and prints every incoming message.

---

## ESP32 Arduino Library

An Arduino library for ESP32 devices is available separately as `SecureChatClient`. It provides the same connect / subscribe / publish / receive API for embedded devices.

**Installation:** Add `SecureChatClient_ESP32.zip` via Arduino IDE → Sketch → Include Library → Add .ZIP Library.

**Dependency:** [ArduinoJson](https://arduinojson.org/) by Benoit Blanchon (install via Library Manager).

```cpp
#include <WiFi.h>
#include "SecureChatClient.h"

SecureChatClient chat("192.168.1.100", 9000, "device_token_1");

void onMessage(const char* room, const char* from,
               const char* data, unsigned long ts) {
    Serial.println(data);
}

void setup() {
    WiFi.begin("SSID", "PASSWORD");
    while (WiFi.status() != WL_CONNECTED) delay(500);

    chat.onMessage(onMessage);
    chat.connect();
    chat.subscribe("factory");
}

void loop() {
    chat.loop();
    chat.publishValue("factory", "temperature", 34.5, 1);
    delay(1000);
}
```

---

## TLS / Security

| Mode | How to enable | Use case |
|---|---|---|
| Insecure (skip verification) | Default on Python client and ESP32 library | Development, trusted LAN |
| Self-signed cert | `openssl` commands in Setup above | Internal networks |
| CA-signed cert | Replace `certs/` with CA-issued files | Production / internet-facing |

For production, distribute your CA certificate to all devices and enable full certificate verification on the client side.

---

## Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `9000` | TCP port |
| `MAX_MESSAGE_SIZE` | `4096` | Max message length in bytes |
| `QUEUE_SIZE` | `200` | Per-client send queue depth |
| `RATE_LIMIT_MESSAGES` | `10` | Messages allowed per window |
| `RATE_LIMIT_WINDOW` | `5` | Rate-limit window in seconds |

---

## License

Open Source. See `LICENSE` for details.
