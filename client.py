"""ConnectRPC クライアント実装."""

import asyncio

from hello_pb2 import HelloRequest
from hello_connect import HelloServiceClient

# サーバーのエンドポイント URL
HELLO_SERVICE_URL = "http://localhost:8000"


async def call_hello():
    """HelloService を呼び出す."""
    async with HelloServiceClient(HELLO_SERVICE_URL) as client:
        req = HelloRequest(name="another microservice")
        res = await client.say_hello(req)
        print(res.message)  # => "Hello, another microservice!"


if __name__ == "__main__":
    asyncio.run(call_hello())
