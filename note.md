# REST に全部賭けたあなたのためのRemote Procedure Call 入門

- 想定読者: RPC に興味がある開発者
- 前提知識: REST API の基本的な理解

## Remote Procedure Call (RPC)

Remote Procedure Call（RPC）は、ネットワーク越しにある関数を、自分のプログラム内の関数と同じように呼び出せるようにする仕組みです。
クライアントとサーバーの通信を、手続き呼び出し（Procedure Call）という抽象化で隠し、リクエストの送受信を意識せずに機能を利用できるようにします。

例えば、ローカルコードで次のような関数呼び出しを行っている場合を考えてみましょう。

```python
user = get_user(123)
```

この `get_user()` が実際にはネットワークを越えてサーバー上で実行されても、呼び出し側からは通常の関数と変わりなく見えるのが RPC の特徴です。

RPC 自体は古くからあり、初期は

- TCP 上の独自プロトコル（ONC RPC など）
- OS や言語専用の RPC（Java RMI など）

が主流でした。しかし、多様な環境に対応しづらいという課題があり、その解決策として HTTP を利用したクロスプラットフォーム対応の RPC が発展してきました。

### HTTP ベース RPC の特徴

近年の RPC は HTTP をトランスポートとして利用する方式が主流となっています。特に Web アプリケーション環境では、HTTP によるメリットがあります。

- 既存の Web インフラが使える（ロードバランサ、トレース、認証、監視など）
- ファイアウォールやブラウザとの親和性
- REST API に慣れた開発者が学習しやすい

gRPC や ConnectRPC は HTTP RPC の代表的な例です。

## REST との比較

RPC は、クライアントがサーバー上の関数を呼び出すアプローチであり、リソース指向の REST とは設計思想が大きく異なります。
ここでは、リソース指向と手続き指向の軸をもとに、両者の違いを整理します。 

| 観点 | REST | RPC |
|------|------|-----|
| 基本概念 | リソース（データ）の操作 | 手続き（機能）の実行 |
| URI | `/users/123` (リソースを表す) | `/UserService.GetUser` (メソッドを表す) |
| 操作 | HTTP メソッドに従う（GET, POST, PUT, DELETE） | 自由にメソッド定義（関数名ベース, 基本 HTTP POST で通信） |
| 状態表現 | 状態の CRUD が中心 | 行動・処理が中心 |
| ステータスコード | 404 Not Found, 200 OK など HTTP ステータスを活用 | レスポンス内のエラー情報 (`code`, `error`) で表現するのが一般的 |

REST は「何に対して何をしたいか」が URI と HTTP メソッドで表現されますが、
RPC は「どの機能を実行したいか」をメソッド名で表現します。

例：
- REST: `GET /users/123`
- RPC: `GetUser(123)`

### データ形式と契約 (Contract) の違い

| 項目 | REST | RPC |
|------|------|-----|
| データ形式 | JSON 等（疎な型定義） | Protocol Buffers 等 (厳密な型定義) |
| 契約（仕様）共有 | ドキュメント依存になりがち | IDL による明確な契約が前提 |
| 自動生成 | 追加ツールが必要 | IDL からコード生成 |

REST ではサーバー実装が先行しがちで、クライアントはドキュメントを基に手動で対応することも多いです。
一方、RPC は IDL による厳密な契約共有が前提となります。

### ステータスとエラーハンドリングの違い

REST のエラーは HTTP ステータスコードで表現するのが基本です。
一方、RPC ではアプリケーションレベルでのステータス管理が一般的であり、HTTP ステータスは一定ルールで固定化される場合もあります。

### 結局、どちらを選ぶべきか？

**REST が適しているケース**

- データ（リソース）の取得、保存、更新、削除が中心: CRUD 操作を HTTP メソッドに自然にマッピングできる
- ブラウザや外部パートナー向け API を提供したい: 広く普及しており、デバッグやトラブルシュートしやすい
- 公開 API で仕様の理解を優先したい: URI が示す意味が明確でドキュメントなしでも推測しやすい
- キャッシュ・検索・認可など Web 既存インフラを最大活用したい: HTTP のリソース指向モデルと相性が良い

**RPC が適しているケース**

- データ操作より「動作」や「処理」が主役の API を提供したい: メソッドを柔軟に定義できる
- マイクロサービス間などの内部通信で性能が重要: バイナリ転送とスキーマによる高速で型安全な通信
- 強いスキーマ管理・自動コード生成で開発ミスを減らしたい: Contract-first 開発
- ストリーミングや双方向通信が必要: REST では難しいユースケース

経験則としては、外部公開は REST、内部通信は RPC を選ぶケースが多いようです。
外部公開する API は将来の利用者が読める URI 設計が重要である一方、内部は性能と信頼性、型による整合性が重視されるというのが理由です。

## Interface Definition Language とコード生成

RPC では、クライアントとサーバー間で呼び出すメソッド名や引数・戻り値の構造を正しく共有する必要があります。
そこで重要になるのが Interface Definition Language (IDL) です。

IDL は、通信インターフェイスを言語に依存せずに定義する仕組みであり、
RPC では事実上の契約（Contract）として扱われます。

### Contract-first とは

API の設計方法には、

- Contract-first: 先に IDL でインターフェイス（契約）を定義し、それをもとにコード生成する
- Code-first: 実装に合わせて API 仕様を後からまとめる

の 2 つのアプローチがあります。RPC では Contract-first が一般的であり、次のような利点があります

- クライアントとサーバが統一された仕様を共有できる
- 仕様が先にあるため、設計の破綻が起きにくい
- 多言語環境での開発がスムーズ

### Protocol Buffers

gRPC や ConnectRPC では、IDL として Protocol Buffers (Protobuf) が広く使われています。Protobuf は Google によって開発されたシリアライズフォーマットであり、以下のような特徴があります

- データ構造（メッセージ）と RPC メソッドを定義できる
- バイナリ形式で高速・軽量
- Protobuf ファイル (.proto) から多言語向けコードを自動生成

たとえば、次のような定義を `.proto` ファイルで記述します

```proto
message GetUserRequest {
  int64 id = 1;
}

message User {
  int64 id = 1;
  string name = 2;
}

service UserService {
  rpc GetUser(GetUserRequest) returns (User);
}
```

### コード生成の主なメリット

IDL からコードを生成することで、開発者はエンドポイント定義と実装に集中できます。主な利点は以下の通りです。

- 型安全性: メソッド引数やレスポンスが型で保証される
- 実装ミスの防止: IDL とコードの乖離が起きにくい
- 多言語対応: 1つの定義から各言語のクライアント/サーバーコード生成
- 保守性の向上: 仕様変更時も自動的にコードへ反映
- ドキュメントの生成が容易: API 仕様として人やツールが参照可能

特に、複数サービスが連携するマイクロサービス環境での効果は大きく、契約（Contract）に基づく整合性の取れた開発が実現できます。

## gRPC

gRPC は、Google によって開発された 高速かつ型安全な RPC フレームワークです。HTTP/2 をベースとし、データ形式には Protocol Buffers（Protobuf）を採用しています。

### gRPC の概要

gRPC は以下の技術を基盤としています

- HTTP/2: 多重化、ヘッダ圧縮、双方向ストリーミング
- Protobuf: バイナリ形式で軽量・高速、IDL としても利用

`.proto` ファイルで RPC メソッドとメッセージを定義し、そこから自動生成されたコードを使ってクライアントとサーバを実装します。

### gRPC の強み

gRPC が広く採用されている理由は、性能と型安全性にあります。

- 高速・低レイテンシ: バイナリ通信 + HTTP/2 の特性による効率性
- 双方向ストリーミング: 一括レスポンスではなく逐次データ送信が可能
- 多言語対応: Protobuf によるコード生成で多数の言語をサポート
- 契約の一元管理: IDL による Contract-first 開発
- マイクロサービスとの相性: スキーマによる疎結合・高可用性

特に、リアルタイム通信やサービス間通信での利用に適しています。

### gRPC の課題

一方で、gRPC には Web 環境での利用に課題があります。

- ブラウザから直接呼び出しにくい: HTTP/2 の仕様やバイナリ形式により制約あり
- gRPC-Web が必要: Envoy 等の変換プロキシが必要になる
- デバッグ性が REST より劣る: バイナリ形式のため、通信内容の可視性が低い
- HTTP/1.1 環境との互換性が低い: レガシー環境対応が困難

特にフロントエンド開発者にとって「手軽に使えない」という壁があり、これが gRPC 普及の妨げにもなっています。この課題を解決するためのアプローチの 1 つとして、ConnectRPC が登場しました。

## ConnectRPC

ConnectRPC は、gRPC の強みはそのままに、Web で扱いやすい形へ進化させた RPC フレームワークです。
Protocol Buffers と gRPC のインターフェイスを踏襲しつつ、開発体験をよりシンプルにすることを目指して設計されています。

### ConnectRPC の概要と設計思想

ConnectRPC のコアコンセプトは次の 3 点に集約されます

1. シンプルな HTTP RPC
2. どのクライアントからでもアクセスできる API
3. 明確な仕様と開発者体験の向上

ConnectRPC は、REST API に近い操作性を保ちつつ、RPC としての型安全性・効率性・ストリーミングを実現しているのが特徴です。

### gRPC との互換性

ConnectRPC は gRPC と高い互換性を持ちます。IDL や RPC メソッド定義は gRPC と同じ Protobuf を使用し、ストリーミングやクライアント・サーバ自動生成にも対応しています。
既存の `.proto` ファイルがそのまま利用できるため、gRPC プロジェクトからの移行がスムーズです。

### Web 対応と HTTP/1.1 対応

gRPC の弱点だった Web とレガシー環境への対応を ConnectRPC は綺麗に解消しています。

- ブラウザ対応: 追加プロキシ不要で Web から直接呼び出せる
- HTTP/1.1 対応: HTTP/2 が利用できない環境にも適用可能
- デバッグ性向上: JSON での通信も可能。curl 等で簡単に検証できる
- 互換性の柔軟性: gRPC, gRPC-Web, Connect 独自プロトコルを選択可能

特に、gRPC-Web ゲートウェイが不要になる点が大きく、Web フロントエンドやモバイルアプリからの利用が非常に楽になります。

## 実装例（バックエンド, Python）

最後に、ConnectRPC を使ったバックエンド実装例を示します。ここでは Python を使用します。
題材として、「名前を渡すと挨拶を返す `HelloService`」を作成します。

### 前提

- Python 3.8 以上
- uv: Python 用の軽量パッケージマネージャー
- [Buf CLI](https://buf.build/docs/cli/installation/): Protobuf と ConnectRPC のコード生成に使用します。

ConnectRPC の Python 実装は、`connect-python` パッケージを使用します。

```bash
$ uv add connect-python protobuf uvicorn
```

### 1. Protobuf 定義の作成

`proto/hello.proto` ファイルを作成し、以下の内容を記述します。

```proto
syntax = "proto3";

package example.v1;

// リクエストメッセージ
message HelloRequest {
  string name = 1;
}

// レスポンスメッセージ
message HelloResponse {
  string message = 1;
}

// RPC サービス
service HelloService {
  rpc SayHello(HelloRequest) returns (HelloResponse);
}
```

このファイルには、

- IDL（インターフェイス定義）
- メッセージ構造
- RPC メソッド

がまとまって定義されています。

### 2. コード生成

次に、Buf のリモートプラグインを使って Python 用のクライアント/サーバースタブを作成しましょう。

`buf.gen.yaml` ファイルをプロジェクトルートに作成します。

```yaml
version: v2
plugins:
  # Protobuf 本体（Python）
  - remote: buf.build/protocolbuffers/python
    out: .

  # 型ヒント（.pyi）
  - remote: buf.build/protocolbuffers/pyi
    out: .

  # ConnectRPC (Python) 用のコード生成
  - remote: buf.build/connectrpc/python
    out: .
```

`buf.yaml`（モジュール設定）も作成しましょう。

```yaml
version: v2
modules:
    - path: proto
```

ここまでのファイルを作成できたら、以下のコマンドを実行してコードを生成します。

```bash
$ buf generate
```

これで、以下のようなファイルが作成されます。

- `hello_pb2.py`: Protobuf メッセージクラス
- `hello_pb2.pyi`: 型ヒント
- `hello_connect.py`: ConnectRPC 用のサービスクラス、ASGI アプリケーション

`hello_connect.py` には、以下のクラスが実装されています。

- `HelloService`: サービスが継承する基底クラス
- `HelloServiceASGIApplication`: ASGI アプリを作成するヘルパー

### 3. ConnectRPC サーバー実装

次に、作成されたクラスを使ってサーバー実装を行います。`server.py` ファイルを作成し、以下の内容を記述します。

```python
# server.py
from connectrpc.request import RequestContext

from hello_pb2 import HelloRequest, HelloResponse
from hello_connect import HelloService, HelloServiceASGIApplication


class MyHelloService(HelloService):
    # .proto の rpc 名 "SayHello" に対応して、メソッド名は snake_case の say_hello になる
    async def say_hello(
        self,
        request: HelloRequest,
        ctx: RequestContext,
    ) -> HelloResponse:
        # 単純にメッセージを組み立てて返すだけ
        return HelloResponse(message=f"Hello, {request.name}!")


# ConnectRPC が提供する ASGI アプリケーションを生成
app = HelloServiceASGIApplication(MyHelloService())
```

この `app` は ASGI アプリ なので、`uvicorn` や `hypercorn` など任意の ASGI サーバーで動かせます。

### 4. サーバー起動

ここでは `uvicorn` を使ってサーバーを起動します。

```bash
$ uvicorn server:app --host 0.0.0.0 --port 8000
```

これで、ConnectRPC サーバーが `http://localhost:8000` で起動しました。

### 5. cURL を使った動作確認

ConnectRPC の HTTP プロトコルでは、`POST /<package>.<Service>/<Method>` に対して JSON を投げる形でも呼び出せます。この例では

- package: `example.v1`
- service: `HelloService`
- method: `SayHello`

なので、パスは `/example.v1.HelloService/SayHello` となります。

以下のように `curl` でリクエストを送って動作確認を行いましょう。

```bash
$ curl -X POST http://localhost:8000/example.v1.HelloService/SayHello \
    -H "Content-Type: application/json" \
    -d '{"name": "Alice"}'
```

レスポンスとして、以下のような JSON が返ってくれば成功です。

```json
{
  "message": "Hello, Alice!"
}
```

以上で、ConnectRPC を使ったシンプルなバックエンド実装が完了しました。Protobuf による型安全な RPC サービスを、Web フレンドリーな形で提供できることが確認できました。

### 6. マイクロサービス間の通信

最後に、ConnectRPC を使ったマイクロサービス間通信の例を簡単に示します。ここでは、先ほどの `HelloService` を呼び出すクライアントサービスを実装します。

クライアントサービスのレポジトリにも、`buf.gen.yaml` と `buf.yaml` を同様に作成します。
その後、同じ ``proto/hello.proto` ファイルを配置してからコード生成を行います。

```bash
$ buf generate
```

このとき、クライアント用のコードも生成されています。生成物には、以下のようなクライアントクラスが含まれています。

```python
from hello_pb2 import HelloRequest
from hello_connect import HelloServiceClient
```

これを使って、以下のようにクライアントコードを実装することができます。

```python
import asyncio
from hello_pb2 import HelloRequest
from hello_connect import HelloServiceClient

# サービス B のエンドポイント URL
HELLO_SERVICE_URL = "http://hello-service:8000"


async def call_hello():
    # クライアントの生成（コンテキストマネージャーで自動クローズ）
    async with HelloServiceClient(HELLO_SERVICE_URL) as client:
        req = HelloRequest(name="another microservice")
        res = await client.say_hello(req)
        print(res.message)  # => "Hello, another microservice!"


if __name__ == "__main__":
    asyncio.run(call_hello())
```

REST と違って呼び出し時に URI や HTTP ヘッダなどを意識する必要がほとんどなく、`client.say_hello()` のように関数呼び出し感覚で HelloService を利用できるのがポイントです。
REST を使うときはクライアントクラスを自前で実装することがありますが、gRPC や ConnectRPC ではそれが標準で提供されているというイメージです。

## まとめ

この記事では、RPC の基本的な概念を REST API と比較しながら解説しました。
さらに、gRPC と ConnectRPC の特徴や違い、ConnectRPC を使ったバックエンド実装例を示しました。