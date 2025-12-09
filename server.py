"""ConnectRPC サーバー実装."""

from connectrpc.request import RequestContext

from hello_pb2 import HelloRequest, HelloResponse
from hello_connect import HelloService, HelloServiceASGIApplication


class MyHelloService(HelloService):
    """HelloService の実装クラス."""

    async def say_hello(
        self,
        request: HelloRequest,
        ctx: RequestContext,
    ) -> HelloResponse:
        """挨拶を返すメソッド.

        .proto の rpc 名 "SayHello" に対応して、メソッド名は snake_case の say_hello になる
        """
        return HelloResponse(message=f"Hello, {request.name}!")


# ConnectRPC が提供する ASGI アプリケーションを生成
app = HelloServiceASGIApplication(MyHelloService())
