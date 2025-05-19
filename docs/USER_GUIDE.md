# BacklogMCP ユーザーガイド

このガイドでは、BacklogMCPの使用方法について説明します。BacklogMCPは、Backlog SaaSをModel Context Protocol (MCP)経由で操作できるようにするプロジェクトです。

## 目次

- [セットアップと実行](#セットアップと実行)
- [使用例](#使用例)
- [API仕様](#api仕様)
- [トラブルシューティング](#トラブルシューティング)

## セットアップと実行

### 前提条件

- Python 3.10以上
- Docker および Docker Compose
- AWS アカウント（AWSへのデプロイ時）
- Backlog APIキー

### 環境変数

以下の環境変数を設定する必要があります：

```
BACKLOG_API_KEY=your_backlog_api_key
BACKLOG_SPACE=your_backlog_space_name
BACKLOG_PROJECT=your_backlog_project_key
BACKLOG_DISABLE_SSL_VERIFY=false  # オプション：SSL検証を無効にする場合はtrue
```

### ローカル開発環境

Docker Composeを使用して、ローカル開発環境を簡単に構築できます：

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/BacklogMCP.git
cd BacklogMCP

# 環境変数の設定
cp .env.example .env
# .envファイルを編集して必要な情報を入力

# Docker Composeでサービスを起動
docker-compose -f docker/docker-compose.yml up -d

# サービスが http://localhost:8000 で利用可能になります
# MCPサーバーは http://localhost:8000/mcp で利用可能になります
# API ドキュメントは http://localhost:8000/docs で利用可能になります
```

### Poetry による環境のセットアップ

Poetryを使用してプロジェクトの依存関係を管理します。

1.  **Poetryのインストール (未インストールの場合):**
    Poetryの公式ドキュメントでは `pipx` を使ったインストールが推奨されています。

    ```bash
    # pipxをインストール (もし未インストールの場合)
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath

    # pipxを使ってPoetryをインストール
    pipx install poetry
    ```
    *WSL環境など、環境によっては `pipx` が正しく動作するために追加のセットアップが必要な場合があります (例: `python3-venv` パッケージのインストール)。詳細はPoetryおよびpipxの公式ドキュメントを参照してください。*

2.  **Poetry Exportプラグインのインストール:**
    `requirements.txt` 形式でのエクスポート機能を利用するために、`poetry-plugin-export` をインストールします。

    ```bash
    poetry self add poetry-plugin-export
    ```

3.  **依存関係のインストール:**
    プロジェクトルートで以下のコマンドを実行し、依存関係をインストールします。

    ```bash
    poetry install
    ```

4.  **仮想環境の有効化:**
    Poetryが管理する仮想環境を有効化します。

    ```bash
    poetry shell
    ```

5.  **開発サーバーの起動:**
    仮想環境内で開発サーバーを起動します。

    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```

## 使用例

### MCPクライアントからの利用

MCPクライアント（例：Claude Desktop）から以下のようにBacklogMCPを利用できます：

```
# MCPサーバーの追加
サーバー名: BacklogMCP
URL: https://your-deployed-url.example.com/mcp
```

追加後、以下のようなプロンプトでBacklogの操作が可能になります：

```
プロジェクト「ProjectA」の未完了の課題を一覧表示して
```

### FastAPI APIとしての利用

RESTful APIとしても利用可能です：

```bash
# プロジェクト一覧の取得
curl https://your-deployed-url.example.com/api/projects

# 課題の作成
curl -X POST https://your-deployed-url.example.com/api/issues \
  -H "Content-Type: application/json" \
  -d '{"projectId": 1234, "summary": "新しい課題", "description": "詳細説明"}'
```

詳細なAPI仕様は、デプロイ後に `/docs` エンドポイントで確認できます。

### サンプルアプリケーション

`example`ディレクトリには、BacklogMCP APIを使用するサンプルプログラムが含まれています：

1. `main.py` - FastAPIを使用したBacklog API操作のサンプルアプリケーション
2. `api_client_example.py` - ホスティングされたBacklog MCP APIにリクエストを送信するクライアントサンプル

サンプルの実行方法は、`example/README.md`を参照してください。

## API仕様

BacklogMCP APIは、RESTful APIとMCP APIの両方を提供します。

### RESTful API

RESTful APIは、以下のエンドポイントを提供します：

- `/api/projects` - プロジェクト関連のエンドポイント
- `/api/issues` - 課題関連のエンドポイント
- `/api/users` - ユーザー関連のエンドポイント
- `/api/priorities` - 優先度関連のエンドポイント
- `/api/bulk-operations` - 一括操作関連のエンドポイント

詳細なAPI仕様は、デプロイ後に `/docs` エンドポイントで確認できます。

### MCP API

MCP APIは、以下のツールとリソースを提供します：

#### プロジェクト管理ツール
- `get_projects` - プロジェクト一覧の取得
- `get_project` - 特定のプロジェクトの取得

#### 課題管理ツール
- `get_issues` - 課題一覧の取得
- `create_issue` - 課題の作成
- `get_issue` - 課題の詳細取得
- `update_issue` - 課題の更新
- `delete_issue` - 課題の削除
- `add_comment` - コメントの追加
- `get_comments` - コメント一覧の取得

#### 一括操作ツール
- `bulk_update_status` - 複数課題のステータス一括更新
- `bulk_update_assignee` - 複数課題の担当者一括更新

#### マスタデータリソース
- `users` - ユーザー一覧
- `priorities` - 優先度一覧
- `statuses` - ステータス一覧
- `categories` - カテゴリー一覧
- `milestones` - マイルストーン一覧
- `versions` - 発生バージョン一覧

## E2Eテスト

E2Eテスト（End-to-End Test）は、アプリケーション全体の動作を実際のユーザーの視点でテストするものです。BacklogMCPでは、Docker環境を使用したE2Eテスト方法を採用しています。

### Docker環境でのE2Eテスト

Docker Composeを使用してBacklogMCPサーバーをコンテナ上で実行し、E2Eテストを行います。この方法は、開発環境やCI/CD環境で安定したテスト実行を可能にします。

詳細な使用方法については、[Docker環境でのE2Eテスト実行ガイド](DOCKER_E2E_TESTING.md)を参照してください。

### E2Eテストの実行に必要な環境設定

E2Eテストを実行するには、以下の環境変数を設定する必要があります：

```
BACKLOG_API_KEY=your_backlog_api_key
BACKLOG_SPACE=your_backlog_space_name
BACKLOG_PROJECT=your_backlog_project_key
```

これらの環境変数は、`.env`ファイルに記述するか、環境変数として直接設定することができます。

環境変数が設定されていない場合、BacklogのAPIを使用するE2Eテストは自動的にスキップされます。

## トラブルシューティング

### よくある問題と解決策

1. **APIキーの認証エラー**
   - Backlog APIキーが正しく設定されているか確認してください
   - APIキーに適切な権限が付与されているか確認してください

2. **環境変数の設定問題**
   - `.env`ファイルが正しく設定されているか確認してください
   - 環境変数が正しく読み込まれているか確認してください

3. **Docker関連の問題**
   - Dockerが正しくインストールされているか確認してください
   - Docker Composeが正しくインストールされているか確認してください
   - ポート8000が他のアプリケーションで使用されていないか確認してください

4. **依存関係の問題**
   - Poetryが正しくインストールされているか確認してください
   - 依存関係が正しくインストールされているか確認してください

### サポート

問題が解決しない場合は、以下の方法でサポートを受けることができます：

1. GitHubのIssueを作成する
2. プロジェクトのメンテナーに連絡する
