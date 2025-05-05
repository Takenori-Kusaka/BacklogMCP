# BacklogMCP

BacklogMCPは、Backlog SaaSをModel Context Protocol (MCP)経由で操作できるようにするプロジェクトです。生成AIモデルがBacklogの機能やデータに簡単にアクセスできるようになり、タスク管理、課題追跡、プロジェクト管理などの操作を自動化することができます。

## 概要

BacklogMCPは以下の特徴を持っています：

- **MCPサーバー**: BacklogのAPIをMCPプロトコルに変換し、生成AIモデルからのアクセスを可能にします
- **スケーラブルなアーキテクチャ**: AWS Lambda上でホストされ、CloudfrontとAPI Gatewayを組み合わせた高性能な構成
- **FastAPIベース**: FastAPIを使用したMCPサーバーで、RESTful APIとしても利用可能
- **柔軟なデプロイオプション**: AWS Lambda、ローカル環境、ECSなど様々な環境で動作可能
- **コンテナ対応**: DockerfileとDocker Composeによる簡単なセットアップと開発
- **包括的なテスト戦略**: ユニットテスト、結合テスト、E2Eテストなど6つのレベルのテスト
- **TDD開発方針**: テストファーストの開発アプローチによる高品質なコード

## アーキテクチャ

BacklogMCPは以下のコンポーネントで構成されています：

```
                                  ┌─────────────┐
                                  │             │
                                  │  CloudFront │
                                  │             │
                                  └──────┬──────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                  API Gateway (REST API)                     │
│                                                             │
└───────────────────────────────┬─────────────────────────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │               │
                        │ AWS Lambda    │
                        │ ┌───────────┐ │
                        │ │ FastAPI   │ │
                        │ │ MCP Server│ │
                        │ └───────────┘ │
                        │               │
                        └───────┬───────┘
                                │
                                ▼
                          ┌──────────┐
                          │          │
                          │ Backlog  │
                          │   API    │
                          │          │
                          └──────────┘
```

- **CloudFront**: コンテンツ配信とキャッシュを担当
- **API Gateway**: トラフィックの分散と管理、APIキー認証、使用量プラン管理
- **AWS Lambda**: FastAPIベースのMCPサーバーを実行（Lambda Web Adapter使用）
- **FastAPI MCP Server**: BacklogのAPIをMCPプロトコルに変換
- **Backlog API**: Backlogの機能にアクセスするためのAPI

## 技術スタック

- **Python 3.10+**: ベースとなるプログラミング言語
- **FastAPI 0.115.12+**: 高性能なWebフレームワーク
- **Pydantic 2.11.3+**: データバリデーションとシリアライゼーション
- **fastapi-mcp 0.3.3+**: FastAPIエンドポイントをMCPツールとして公開するライブラリ
- **Uvicorn 0.34.2+**: ASGIサーバー
- **Mangum 0.19.0+**: AWS Lambda用のASGIアダプター
- **AWS Lambda Web Adapter**: WebアプリケーションをLambda上で実行するためのアダプター
- **Docker & Docker Compose**: コンテナ化と開発環境のセットアップ
- **AWS CDK**: インフラストラクチャのコード化と管理
- **AWS サービス**: Lambda、CloudFront、API Gateway、ECR、ECS（オプション）

## 機能

BacklogMCPは以下のBacklog機能へのアクセスを提供します：

### プロジェクト管理
- プロジェクト一覧の取得
- 特定のプロジェクトの取得

### 課題管理
- 課題一覧の取得（フィルタリング機能付き）
- 課題の作成
- 課題の詳細取得
- 課題の更新
- 課題の削除
- コメントの追加
- コメント一覧の取得

### 一括操作
- 複数課題のステータス一括更新
- 複数課題の担当者一括更新

### マスタデータ管理
- ユーザー一覧の取得
- 優先度一覧の取得
- ステータス一覧の取得
- カテゴリー一覧の取得
- マイルストーン一覧の取得
- 発生バージョン一覧の取得

これらの機能は、MCPのツールとリソースとして公開され、生成AIモデルから簡単にアクセスできます。

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

### Poetry による開発環境のセットアップ

```bash
# Poetryのインストール（未インストールの場合）
pip install poetry

# 依存関係のインストール
poetry install

# 仮想環境の有効化
poetry shell

# 開発サーバーの起動
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### AWS Lambdaへのデプロイ

AWS CDKを使用して、AWSにデプロイすることができます：

```bash
# CDKディレクトリに移動
cd cdk

# 依存関係のインストール
npm install

# AWSアカウントの設定
aws configure

# CDKのデプロイ
cdk deploy
```

## テスト戦略

BacklogMCPは、以下の6つのレベルでテストを実施します：

1. **Unitテスト**: 個々の関数やメソッドが期待通りに動作することを確認
2. **結合テスト**: 複数のコンポーネントが連携して正しく動作することを確認
3. **E2Eテスト**: システム全体が実際の環境に近い状態で正しく動作することを確認
4. **デプロイテスト**: コンテナ化された環境でシステムが正しく動作することを確認
5. **CIテスト**: コードの変更がマージされる前に、自動的にテストを実行して品質を確保
6. **CDテスト**: デプロイされた環境が正しく動作することを確認

テストを実行するには：

```bash
# 依存関係のインストール
poetry install

# すべてのテストの実行
pytest

# 特定のテストレベルの実行
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# カバレッジレポートの生成
pytest --cov=app

# テスト実行スクリプトを使用する場合
python scripts/run_tests.py --unit      # ユニットテストのみ実行
python scripts/run_tests.py --integration  # 統合テストのみ実行
python scripts/run_tests.py --e2e       # E2Eテストのみ実行
python scripts/run_tests.py --coverage   # カバレッジレポートを生成
python scripts/run_tests.py --verbose    # 詳細な出力
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

## 開発

### プロジェクト構造

```
BacklogMCP/
├── app/                  # FastAPIアプリケーション
│   ├── application/      # アプリケーション層（ユースケース、サービス）
│   ├── infrastructure/   # インフラ層（DB, API, 外部サービス連携）
│   ├── presentation/     # プレゼンテーション層（APIエンドポイント、MCPツール）
│   └── main.py           # アプリケーションのエントリーポイント
├── tests/                # テスト
│   ├── unit/             # ユニットテスト
│   ├── integration/      # 統合テスト
│   └── e2e/              # エンドツーエンドテスト
├── scripts/              # スクリプト
├── .github/              # GitHub関連の設定
├── cdk/                  # AWS CDKコード
├── docker/               # Docker関連ファイル
└── README.md             # このファイル
```

### 開発方針

#### TDD開発方針
- すべての新規機能・修正は「テストファースト」（テスト→実装→リファクタ）で開発
- テストは以下の3つのレベルに分類
  - `tests/unit/`: ユニットテスト（単一のクラスや関数のテスト）
  - `tests/integration/`: 統合テスト（複数のコンポーネントの連携テスト）
  - `tests/e2e/`: エンドツーエンドテスト（ユーザー視点での機能テスト）
- FastAPIのエンドポイントも必ずテストを作成
- pytestを標準とし、カバレッジ計測をCIで必須化

#### Poetry/uv関連ルール
- 利用するパッケージは可能な限り最新化すること
- 依存関係の管理はPoetryを使用すること
- パッケージのインストールはuvを使用して高速化すること
- pyproject.tomlに全ての依存関係を記述すること
- 仮想環境はPoetryで管理すること

#### 型チェック・バリデーションルール
- すべてのコードは型アノテーションや型チェックを必須とし、型エラーを回避するためにany型や型無視（type: ignore等）を安易に使用してはならない。型安全性を維持すること。

#### テスト失敗時の対応ルール
- テストで失敗が発生した場合、テストをスキップ（skip）したり、passやassert True等で無意味に通過させるのではなく、テストの意義を確認し、必要に応じて実装やテスト自体を修正し、正しくテストが通る状態にすること。

## E2Eテスト

E2Eテスト（End-to-End Test）は、アプリケーション全体の動作を実際のユーザーの視点でテストするものです。BacklogMCPでは、以下の2種類のE2Eテストをサポートしています：

1. **モックを使用したE2Eテスト**：実際のBacklog APIに接続せず、モックを使用してテストします。CI/CD環境や、Backlog APIの認証情報がない環境でも実行できます。

2. **実際のBacklog APIに接続するE2Eテスト**：実際のBacklog APIに接続してテストします。より現実的なテストが可能ですが、Backlog APIの認証情報が必要です。

### E2Eテストの実行に必要な環境設定

実際のBacklog APIに接続するE2Eテストを実行するには、以下の環境変数を設定する必要があります：

```
BACKLOG_API_KEY=your_backlog_api_key
BACKLOG_SPACE=your_backlog_space_name
BACKLOG_PROJECT=your_backlog_project_key
```

これらの環境変数は、`.env`ファイルに記述するか、環境変数として直接設定することができます。

環境変数が設定されていない場合、実際のBacklog APIに接続するE2Eテストは自動的にスキップされます。

## AWS CDKによるデプロイ

BacklogMCPは、AWS CDKを使用してAWS環境にデプロイすることができます。デプロイアーキテクチャは、CloudFront + API Gateway + Lambda（Web Adapter）を使用したFastAPIホスティングアーキテクチャです。

### デプロイアーキテクチャの特徴

- **Lambda Web Adapter**: 既存FastAPIコードの変更不要、ASGI互換性
- **CloudFront**: グローバルキャッシュ、WAF連携、カスタムドメイン管理
- **API Gateway REST**: 使用量プラン管理、APIキー認証、リクエストバリデーション
- **CDK構成**: インフラのコード化、マルチリージョン展開可能性

詳細なデプロイ方法や設定については、`cdk/README.md`を参照してください。

## ユースケース網羅性について

本プロジェクトは、Backlogの主要なユースケースを網羅的にサポートすることを目的としています。詳細なユースケースは `BacklogUsecases.md` にまとめられており、以下のカテゴリに分類されます：

- チケット（課題）の基本操作（作成・編集・削除・ファイル管理・コメント・通知など）
- チケットの管理と整理（分類・進捗管理・視覚的管理ツール）
- チケットの検索と分析（検索・フィルタ・集計・分析）
- チームコラボレーション（Wiki・ドキュメント・コメント・通知・進捗共有）
- プロジェクト管理（プロジェクト設定・スケジュール・リソース管理）
- セキュリティと権限管理（アクセス制御・ユーザー管理）
- システム連携と自動化（API・外部ツール・定期実行）
- モバイル活用（モバイルアプリ・通知・タスク管理）
- 高度な業務フロー（ワークフロー・リスク管理・プロジェクト評価）

これらのユースケースに対し、BacklogMCPはMCPツール・APIとして包括的なサポートを提供します。詳細なユースケースや機能要件は `BacklogUsecases.md` を参照してください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 貢献

貢献は歓迎します！バグ報告、機能リクエスト、プルリクエストなど、どんな形の貢献も大歓迎です。

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成
