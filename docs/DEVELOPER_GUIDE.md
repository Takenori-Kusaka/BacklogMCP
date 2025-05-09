# BacklogMCP 開発者ガイド

このガイドでは、BacklogMCPの開発に関する情報を提供します。アーキテクチャ、開発方針、プロジェクト構造などについて説明します。

## 目次

- [アーキテクチャ](#アーキテクチャ)
- [技術スタック](#技術スタック)
- [プロジェクト構造](#プロジェクト構造)
- [開発方針](#開発方針)
- [テスト戦略](#テスト戦略)
- [コーディング規約](#コーディング規約)

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

### アーキテクチャの特徴

- **クリーンアーキテクチャ**: 依存関係の方向を制御し、ビジネスロジックを技術的な実装から分離
- **ヘキサゴナルアーキテクチャ**: ポートとアダプターを使用して外部システムとの連携を抽象化
- **レイヤードアーキテクチャ**: プレゼンテーション層、アプリケーション層、インフラストラクチャ層に分離
- **依存性の注入**: 疎結合なコンポーネント間の関係を実現
- **リポジトリパターン**: データアクセスを抽象化し、ビジネスロジックから分離

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

## プロジェクト構造

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
└── README.md             # プロジェクト概要
```

### 主要なディレクトリとファイル

#### app/application/

アプリケーション層には、ビジネスロジックとユースケースが含まれています。

- `services/`: ビジネスロジックを実装するサービスクラス
  - `issue_service.py`: 課題関連のビジネスロジック
  - `project_service.py`: プロジェクト関連のビジネスロジック
  - `bulk_operations_service.py`: 一括操作関連のビジネスロジック

#### app/infrastructure/

インフラストラクチャ層には、外部システムとの連携を担当するコードが含まれています。

- `backlog/`: Backlog APIとの連携
  - `backlog_client.py`: Backlog APIクライアント
  - `backlog_client_wrapper.py`: クライアントのラッパー

#### app/presentation/

プレゼンテーション層には、APIエンドポイントとMCPツールが含まれています。

- `api/`: RESTful APIエンドポイント
  - `issue_router.py`: 課題関連のエンドポイント
  - `project_router.py`: プロジェクト関連のエンドポイント
  - `bulk_operations_router.py`: 一括操作関連のエンドポイント
  - `user_router.py`: ユーザー関連のエンドポイント
  - `priority_router.py`: 優先度関連のエンドポイント
- `mcp/`: MCPツールとリソース
  - `issue_tools.py`: 課題関連のMCPツール
  - `project_tools.py`: プロジェクト関連のMCPツール
  - `bulk_operations_tools.py`: 一括操作関連のMCPツール

## 開発方針

### TDD開発方針
- すべての新規機能・修正は「テストファースト」（テスト→実装→リファクタ）で開発
- テストは以下の3つのレベルに分類
  - `tests/unit/`: ユニットテスト（単一のクラスや関数のテスト）
  - `tests/integration/`: 統合テスト（複数のコンポーネントの連携テスト）
  - `tests/e2e/`: エンドツーエンドテスト（ユーザー視点での機能テスト）
- FastAPIのエンドポイントも必ずテストを作成
- pytestを標準とし、カバレッジ計測をCIで必須化

### Poetry/uv関連ルール
- 利用するパッケージは可能な限り最新化すること
- 依存関係の管理はPoetryを使用すること
- パッケージのインストールはuvを使用して高速化すること
- pyproject.tomlに全ての依存関係を記述すること
- 仮想環境はPoetryで管理すること
- 依存パッケージのバージョン不整合が発生した場合は、FastAPIのバージョンをコアとし、他の依存パッケージ（例：pydantic, uvicorn等）はFastAPIの互換性に合わせて調整すること

### 型チェック・バリデーションルール
- すべてのコードは型アノテーションや型チェックを必須とし、型エラーを回避するためにany型や型無視（type: ignore等）を安易に使用してはならない。型安全性を維持すること。

### テスト失敗時の対応ルール
- テストで失敗が発生した場合、テストをスキップ（skip）したり、passやassert True等で無意味に通過させるのではなく、テストの意義を確認し、必要に応じて実装やテスト自体を修正し、正しくテストが通る状態にすること。

## AWS CDK

BacklogMCPはAWS CDKを使用してインフラストラクチャをコード化しています。CDKプロジェクトは`cdk/`ディレクトリに配置されています。

### CDKプロジェクト構造

```
cdk/
├── bin/                  # CDKアプリケーションのエントリーポイント
│   ├── app.ts            # CDKアプリケーションの定義
│   └── cdk.ts            # CDKコマンドラインツールのエントリーポイント
├── lib/                  # CDKスタックの定義
│   └── backlog-mcp-stack.ts  # BacklogMCPのインフラスタック定義
├── src/                  # TypeScriptソースコード
│   ├── bin/              # ビルド後のエントリーポイント
│   ├── lib/              # ビルド後のスタック定義
│   └── test/             # テストコード
├── test/                 # テストコード
│   └── backlog-mcp.test.ts  # スタックのテスト
├── scripts/              # スクリプト
│   └── run-tests.sh      # テスト実行スクリプト
├── cdk.json              # CDK設定ファイル
├── package.json          # npm設定ファイル
└── tsconfig.json         # TypeScript設定ファイル
```

### CDKスタック

`BacklogMcpStack`は以下のAWSリソースを定義しています：

- **Lambda関数**: FastAPIアプリケーションを実行するためのLambda関数
- **API Gateway**: RESTful APIエンドポイントを提供するためのAPI Gateway
- **CloudFront**: コンテンツ配信とキャッシュを担当するCloudFrontディストリビューション
- **WAF**: セキュリティを強化するためのWAF（Web Application Firewall）
- **CloudWatch**: モニタリングとアラートのためのCloudWatchアラーム
- **SNS**: アラート通知のためのSNSトピック

### CDKテスト

CDKプロジェクトには、以下のテストが含まれています：

- **環境別設定テスト**: 各環境（dev、stg、prod）のスタックが正しく作成されることを確認
- **リソース作成テスト**: 必要なリソースが全て作成されることを確認
- **API Gateway設定テスト**: API Gatewayに必要なリソースとメソッドが作成されることを確認
- **CloudFront設定テスト**: CloudFrontに必要な設定が適用されることを確認
- **スナップショットテスト**: スタックのスナップショットが一致することを確認

テストを実行するには、以下のコマンドを使用します：

```bash
cd cdk
npm test -- --no-watchman
```

または、スクリプトを使用して実行することもできます：

```bash
cd cdk
bash scripts/run-tests.sh
```

> **注意**: テスト実行時に`--no-watchman`オプションを使用することで、Jestのレポーターのエラーを回避できます。

### CDKテストのトラブルシューティング

#### 問題: テスト実行時に「Cannot find module '../lib/backlog-mcp-stack'」エラーが発生する

この問題は、TypeScriptのコンパイル設定で`lib`、`bin`、`test`ディレクトリが除外されているために発生します。

**解決策**: `tsconfig.json`ファイルを修正して、これらのディレクトリを除外しないようにします。

```json
{
  "exclude": [
    "node_modules",
    "cdk.out",
    "dist"
  ]
}
```

#### 問題: テスト実行時に「RangeError: Invalid count value」エラーが発生する

この問題は、Jestのレポーターのバグによって発生します。

**解決策**: テスト実行時に`--no-watchman`オプションを追加します。

```bash
npm test -- --no-watchman
```

または、`scripts/run-tests.sh`スクリプトを修正して、このオプションを追加します。

```bash
npm test -- --no-cache --no-watchman
```

## テスト戦略

BacklogMCPは、以下の6つのレベルでテストを実施します：

1. **Unitテスト**: 個々の関数やメソッドが期待通りに動作することを確認
2. **結合テスト**: 複数のコンポーネントが連携して正しく動作することを確認
3. **E2Eテスト**: システム全体が実際の環境に近い状態で正しく動作することを確認
4. **デプロイテスト**: コンテナ化された環境でシステムが正しく動作することを確認
5. **CIテスト**: コードの変更がマージされる前に、自動的にテストを実行して品質を確保
6. **CDテスト**: デプロイされた環境が正しく動作することを確認

詳細なテスト戦略については、[tests/TEST_STRATEGY.md](../tests/TEST_STRATEGY.md)を参照してください。

## コーディング規約

### Pythonコーディング規約

- **PEP 8**: Pythonの標準的なコーディング規約に従う
- **Black**: コードフォーマッターとしてBlackを使用
- **isort**: インポート文の整理にisortを使用
- **flake8**: コードの静的解析にflake8を使用
- **mypy**: 型チェックにmypyを使用

### コミットメッセージ規約

- **Conventional Commits**: コミットメッセージは[Conventional Commits](https://www.conventionalcommits.org/)の形式に従う
  - `feat`: 新機能
  - `fix`: バグ修正
  - `docs`: ドキュメントのみの変更
  - `style`: コードの意味に影響を与えない変更（空白、フォーマット、セミコロンの欠落など）
  - `refactor`: バグ修正でも新機能の追加でもないコードの変更
  - `perf`: パフォーマンスを向上させるコードの変更
  - `test`: 不足しているテストの追加や既存のテストの修正
  - `chore`: ビルドプロセスやドキュメント生成などの変更

### プルリクエスト規約

- プルリクエストは小さく保ち、1つの機能または修正に焦点を当てる
- プルリクエストには、変更内容の説明と、関連するIssueへの参照を含める
- プルリクエストがマージされる前に、すべてのテストが通過することを確認する
- プルリクエストがマージされる前に、少なくとも1人のレビューアーの承認を得る

## 貢献方法

プロジェクトへの貢献方法については、[CONTRIBUTING.md](CONTRIBUTING.md)を参照してください。
