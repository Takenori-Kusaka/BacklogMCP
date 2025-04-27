# BacklogMCP

BacklogMCPは、Backlog SaaSをModel Context Protocol (MCP)経由で操作できるようにするプロジェクトです。生成AIモデルがBacklogの機能やデータに簡単にアクセスできるようになり、タスク管理、課題追跡、プロジェクト管理などの操作を自動化することができます。

## 概要

BacklogMCPは以下の特徴を持っています：

- **MCPサーバー**: BacklogのAPIをMCPプロトコルに変換し、生成AIモデルからのアクセスを可能にします
- **スケーラブルなアーキテクチャ**: AWS Lambda上でホストされ、CloudfrontとALBを組み合わせた高性能な構成
- **FastAPIベース**: FastAPIを使用したMCPサーバーで、RESTful APIとしても利用可能
- **柔軟なデプロイオプション**: AWS Lambda、ローカル環境、ECSなど様々な環境で動作可能
- **コンテナ対応**: DockerfileとDocker Composeによる簡単なセットアップと開発

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
│                  Application Load Balancer                  │
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
- **Application Load Balancer (ALB)**: トラフィックの分散と管理
- **AWS Lambda**: FastAPIベースのMCPサーバーを実行
- **FastAPI MCP Server**: BacklogのAPIをMCPプロトコルに変換
- **Backlog API**: Backlogの機能にアクセスするためのAPI

## 技術スタック

- **Python 3.10+**: ベースとなるプログラミング言語
- **FastAPI**: 高性能なWebフレームワーク
- **FastAPI-MCP**: FastAPIエンドポイントをMCPツールとして公開するライブラリ
- **PyBacklogPy**: BacklogのAPIをPythonから簡単に呼び出すためのライブラリ
- **AWS Lambda Web Adapter**: WebアプリケーションをLambda上で実行するためのアダプター
- **Docker & Docker Compose**: コンテナ化と開発環境のセットアップ
- **AWS サービス**: Lambda、CloudFront、ALB、ECR、ECS（オプション）

## 機能

BacklogMCPは以下のBacklog機能へのアクセスを提供します：

- **プロジェクト管理**: プロジェクトの作成、更新、削除、一覧取得
- **課題管理**: 課題の作成、更新、削除、検索、コメント
- **Wiki**: Wikiページの作成、更新、削除、閲覧
- **ファイル管理**: ファイルのアップロード、ダウンロード、削除
- **ユーザー管理**: ユーザー情報の取得、プロジェクトメンバーの管理
- **通知**: 課題やWikiの更新通知

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
docker-compose up -d

# サービスが http://localhost:8000 で利用可能になります
# MCPサーバーは http://localhost:8000/mcp で利用可能になります
```

### AWS Lambdaへのデプロイ

AWS CDKを使用して、AWSにデプロイすることができます：

```bash
# 依存関係のインストール
npm install

# AWSアカウントの設定
aws configure

# CDKのデプロイ
cdk deploy
```

または、AWS Management Consoleを使用して手動でデプロイすることもできます。詳細な手順は[デプロイガイド](docs/deployment.md)を参照してください。

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

## 開発

### プロジェクト構造

```
BacklogMCP/
├── app/                  # FastAPIアプリケーション
│   ├── application/      # アプリケーション層（ユースケース、サービス）
│   ├── infrastructure/   # インフラ層（DB, API, 外部サービス連携）
│   ├── presentation/     # プレゼンテーション層（APIエンドポイント、FastAPIルーター）
│   └── main.py           # アプリケーションのエントリーポイント
├── tests/                # テスト
│   ├── unit/             # ユニットテスト
│   ├── integration/      # 統合テスト
│   └── e2e/              # エンドツーエンドテスト
├── requirements/         # 依存関係の定義
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

### テスト

テストを実行するには：

```bash
# 依存関係のインストール
pip install -e ".[dev]"

# すべてのテストの実行
pytest

# 特定のテストレベルの実行
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# カバレッジレポートの生成
pytest --cov=app
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 貢献

貢献は歓迎します！バグ報告、機能リクエスト、プルリクエストなど、どんな形の貢献も大歓迎です。

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 連絡先

質問や提案がある場合は、Issueを作成するか、以下の連絡先までお問い合わせください：

- メール: your.email@example.com
- Twitter: [@yourusername](https://twitter.com/yourusername)

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
