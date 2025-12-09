# ConnectRPC Python デモ

ConnectRPC を使った Python バックエンドの実装例です。

## 前提条件

- Python 3.14 以上
- [uv](https://docs.astral.sh/uv/): Python パッケージマネージャー
- [Buf CLI](https://buf.build/docs/cli/installation/): Protobuf コード生成ツール

## セットアップ

```bash
# 依存パッケージのインストール
uv sync

# Protobuf からコード生成
buf generate
```

## デモの実行方法

### 1. サーバーの起動

```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8000
```

### 2. 動作確認（curl）

別のターミナルで以下を実行：

```bash
curl -X POST http://localhost:8000/example.v1.HelloService/SayHello \
    -H "Content-Type: application/json" \
    -d '{"name": "Alice"}'
```

期待されるレスポンス：

```json
{
  "message": "Hello, Alice!"
}
```

### 3. クライアントからの呼び出し

サーバーが起動している状態で、別のターミナルから実行：

```bash
uv run python client.py
```

期待される出力：

```
Hello, another microservice!
```

## ファイル構成

```
.
├── proto/
│   └── hello.proto      # Protobuf 定義
├── buf.yaml             # Buf モジュール設定
├── buf.gen.yaml         # コード生成設定
├── server.py            # サーバー実装
├── client.py            # クライアント実装
├── hello_pb2.py         # 生成: メッセージクラス
├── hello_pb2.pyi        # 生成: 型ヒント
└── hello_connect.py     # 生成: サービス/クライアントクラス
```
