# Backlog MCP API サンプル

このディレクトリには、Backlog MCP APIを使用するサンプルプログラムが含まれています。

## サンプル一覧

1. `main.py` - FastAPIを使用したBacklog API操作のサンプルアプリケーション
2. `api_client_example.py` - ホスティングされたBacklog MCP APIにリクエストを送信するクライアントサンプル

## 前提条件

- Python 3.8以上
- 必要なパッケージ: `requests`（APIクライアント用）
- Backlog APIキー
- Backlogスペース名
- Backlogプロジェクトキー（オプション）

## 環境変数の設定

サンプルを実行する前に、以下の環境変数を設定してください：

```bash
# Windows (PowerShell)
$env:BACKLOG_API_KEY = "あなたのBacklog APIキー"
$env:BACKLOG_SPACE = "あなたのBacklogスペース名"
$env:BACKLOG_PROJECT = "プロジェクトキー"  # オプション

# Windows (コマンドプロンプト)
set BACKLOG_API_KEY=あなたのBacklog APIキー
set BACKLOG_SPACE=あなたのBacklogスペース名
set BACKLOG_PROJECT=プロジェクトキー  # オプション

# Linux/macOS
export BACKLOG_API_KEY="あなたのBacklog APIキー"
export BACKLOG_SPACE="あなたのBacklogスペース名"
export BACKLOG_PROJECT="プロジェクトキー"  # オプション
```

## サンプルアプリケーションの実行方法

### 1. FastAPIサンプルアプリケーション（main.py）

このサンプルは、FastAPIを使用してBacklog APIを操作するRESTful APIサーバーを提供します。

```bash
# プロジェクトのルートディレクトリから実行
cd example
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

サーバーが起動したら、ブラウザで http://localhost:8080/docs にアクセスして、Swagger UIでAPIを試すことができます。

### 2. APIクライアントサンプル（api_client_example.py）

このサンプルは、ホスティングされたBacklog MCP APIにHTTPリクエストを送信して、Backlogの課題を操作する方法を示します。

```bash
# 必要なパッケージのインストール
pip install requests

# プロジェクトのルートディレクトリから実行
cd example
python api_client_example.py
```

デフォルトでは、APIクライアントはローカルの `http://localhost:8000` にリクエストを送信します。別のURLを使用する場合は、環境変数 `API_BASE_URL` を設定してください：

```bash
# Windows (PowerShell)
$env:API_BASE_URL = "http://your-api-host:port"

# Windows (コマンドプロンプト)
set API_BASE_URL=http://your-api-host:port

# Linux/macOS
export API_BASE_URL="http://your-api-host:port"
```

## Dockerでの実行

プロジェクトのルートディレクトリにある `docker-compose.yml` を使用して、Dockerコンテナでサービスを実行することもできます：

```bash
# プロジェクトのルートディレクトリから実行
docker-compose -f docker/docker-compose.yml up --build
```

サービスが起動したら、APIクライアントサンプルを実行して、ホスティングされたAPIにリクエストを送信できます：

```bash
cd example
python api_client_example.py
```

## サンプルの機能

APIクライアントサンプル（api_client_example.py）は、以下の操作を実行します：

1. プロジェクト一覧の取得
2. プロジェクト詳細の取得
3. ユーザー一覧の取得
4. 優先度一覧の取得
5. ステータス一覧の取得
6. 課題一覧の取得
7. 課題の作成（名前ベースのパラメータを使用）
8. 課題の更新（名前ベースのパラメータを使用）
9. コメントの追加
10. コメント一覧の取得

これらの操作は、Backlog MCP APIを使用して実行されます。各操作の詳細については、サンプルコードのコメントを参照してください。

## 注意事項

- サンプルコードは、環境変数 `BACKLOG_API_KEY` と `BACKLOG_SPACE` が設定されていることを前提としています。
- 課題の種別一覧を取得するエンドポイント（`/projects/{project_key}/issue-types`）は、サンプルアプリケーションに実装されていない場合があります。その場合、サンプルの課題種別が使用されます。
- APIリクエストが失敗した場合、エラーメッセージが表示されます。
