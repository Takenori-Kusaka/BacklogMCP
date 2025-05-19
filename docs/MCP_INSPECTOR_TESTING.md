# MCP Inspectorを使用したE2Eテスト

このドキュメントでは、[MCP Inspector](https://github.com/modelcontextprotocol/inspector)を使用してBacklogMCPサーバーのE2Eテストを実行する方法について説明します。

## 概要

MCP Inspectorは、MCPサーバーのテストと検査を行うためのツールです。このツールを使用することで、MCPサーバーが提供するツールやリソースを簡単にテストできます。

## 前提条件

- Node.js v22.7.5以上
- npm または yarn
- Docker と Docker Compose（サーバーの起動に必要）
- Python 3.8以上（HTMLレポート生成に必要）

## インストール

MCP Inspectorは、npmを使用してインストールできます：

```bash
npm install -g @modelcontextprotocol/inspector
```

または、プロジェクト内にローカルインストールすることもできます：

```bash
npm install @modelcontextprotocol/inspector
```

## 使用方法

### 1. 単一テストの実行

単一のテストを実行するには、以下のコマンドを使用します：

```bash
./scripts/run_inspector_e2e_test.sh [テストメソッド]
```

テストメソッドを指定しない場合は、デフォルトで `tools/list` が実行されます。

### 2. テストスイートの実行

複数のテストを一度に実行するには、テストスイートスクリプトを使用します：

```bash
./scripts/run_inspector_test_suite.sh
```

このスクリプトは、`tests/e2e/mcp_inspector_test_cases.json`に定義されたすべてのテストケースを実行します。テスト結果は、`test-reports/mcp-inspector`ディレクトリに保存され、HTMLレポートも自動的に生成されます。

### 3. 利用可能なテストメソッド

MCP Inspectorでは、以下のようなテストメソッドが利用可能です：

#### 基本テスト
- `tools/list` - 利用可能なツールの一覧を取得
- `resources/list` - 利用可能なリソースの一覧を取得

#### ツールテスト
- `tools/call --tool-name get_projects` - プロジェクト一覧を取得
- `tools/call --tool-name get_project --tool-arg project_key=<プロジェクトキー>` - 特定のプロジェクトを取得
- `tools/call --tool-name get_issues --tool-arg project_key=<プロジェクトキー>` - 課題一覧を取得
- `tools/call --tool-name get_users` - ユーザー一覧を取得
- `tools/call --tool-name get_priorities` - 優先度一覧を取得
- `tools/call --tool-name get_statuses --tool-arg project_key=<プロジェクトキー>` - ステータス一覧を取得

#### リソーステスト
- `resources/get --resource-uri project_info --resource-arg project_key=<プロジェクトキー>` - プロジェクト情報リソースを取得
- `resources/get --resource-uri issue_info --resource-arg project_key=<プロジェクトキー> --resource-arg issue_key=<課題キー>` - 課題情報リソースを取得

### 4. 手動でのテスト実行

MCP Inspectorを直接実行することもできます：

```bash
# ヘッドレスモードでの実行
npx @modelcontextprotocol/inspector http://localhost:8000/mcp --headless --transport streamable-http

# インタラクティブモードでの実行
npx @modelcontextprotocol/inspector http://localhost:8000/mcp
```

インタラクティブモードでは、ブラウザが起動し、GUIを通じてMCPサーバーをテストできます。

## テスト結果の確認

### テキストレポート

テスト実行後、テスト結果のサマリーが表示されます。詳細なテスト結果は、`test-reports/mcp-inspector`ディレクトリに保存されます。

### HTMLレポート

テストスイートを実行すると、HTMLレポートが自動的に生成されます。このレポートは、`test-reports/mcp-inspector/report.html`に保存されます。HTMLレポートには、テスト結果の概要と詳細が含まれています。

HTMLレポートを手動で生成するには、以下のコマンドを使用します：

```bash
./scripts/generate_inspector_report.py --report-dir test-reports/mcp-inspector --output test-reports/mcp-inspector/report.html
```

## 環境変数の設定

認証が必要なテストを実行するには、以下の環境変数を設定する必要があります：

- `BACKLOG_API_KEY` - Backlog APIキー
- `BACKLOG_SPACE` - Backlogスペース名
- `BACKLOG_PROJECT` - Backlogプロジェクトキー
- `BACKLOG_ISSUE` - Backlog課題キー（課題が必要なテストの場合）

これらの環境変数は、`.env`ファイルに設定することもできます：

```
BACKLOG_API_KEY=your_api_key
BACKLOG_SPACE=your_space
BACKLOG_PROJECT=your_project
BACKLOG_ISSUE=your_issue
```

## トラブルシューティング

### ポートが使用中の場合

「Proxy Server PORT IS IN USE at port 6277」というエラーが表示される場合は、以下のコマンドを実行して、使用中のポートを解放してください：

```bash
# Linuxの場合
sudo kill $(lsof -t -i:6277)

# Windowsの場合
netstat -ano | findstr :6277
taskkill /PID <PID> /F
```

### サーバーの起動に失敗する場合

サーバーの起動に失敗する場合は、以下のコマンドを実行して、Dockerコンテナとネットワークを削除してから再試行してください：

```bash
docker-compose -f docker/docker-compose.test.yml down
```

## GitHub Actionsでの自動テスト

このプロジェクトでは、GitHub Actionsを使用してMCP Inspectorのテストを自動的に実行しています。GitHub Actionsワークフローは、以下の機能を提供します：

1. プッシュやプルリクエスト時に自動的にテストを実行
2. 手動でのテスト実行（特定のテストメソッドやテストスイート全体）
3. テスト結果のアーティファクトとしての保存
4. テスト結果の概要表示

詳細は、`.github/workflows/mcp-inspector-test.yml`を参照してください。

## カスタムテストケースの追加

新しいテストケースを追加するには、`tests/e2e/mcp_inspector_test_cases.json`ファイルを編集します。テストケースは、以下のカテゴリに分類されます：

- `basic_tests` - 基本的なテスト（認証不要）
- `tool_tests` - ツールを呼び出すテスト（認証が必要な場合あり）
- `resource_tests` - リソースを取得するテスト（認証が必要な場合あり）
- `error_tests` - エラーケースのテスト

各テストケースには、以下の情報を含める必要があります：

- `name` - テスト名
- `method` - テストメソッド
- `description` - テストの説明
- `requires_auth` - 認証が必要かどうか（オプション、デフォルトはfalse）
- `requires_issue` - 課題が必要かどうか（オプション、デフォルトはfalse）
- `expected_error` - エラーが期待されるかどうか（オプション、デフォルトはfalse）

## 参考リンク

- [MCP Inspector GitHub](https://github.com/modelcontextprotocol/inspector)
- [Model Context Protocol](https://github.com/modelcontextprotocol/mcp)
- [FastAPI](https://fastapi.tiangolo.com/)
