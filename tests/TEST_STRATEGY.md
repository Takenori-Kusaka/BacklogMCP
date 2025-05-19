# BacklogMCP テスト戦略

このドキュメントでは、BacklogMCPプロジェクトのテスト戦略について説明します。テストは以下の6つのレベルで実施します。

## 1. Unitテスト

**目的**: 個々の関数やメソッドが期待通りに動作することを確認する。

**実施方法**:
- 関数単位でテストを実施
- 正常系と異常系の両方をテスト
- 境界値テストを含める
- モックを使用して外部依存を排除
- 例外処理のテストを含める
- 高いコードカバレッジを目指す（目標: 90%以上）

**ディレクトリ**: `tests/unit/`

**実行コマンド**: `pytest tests/unit/`

## 2. 結合テスト (Integration Test)

**目的**: 複数のコンポーネントが連携して正しく動作することを確認する。

**実施方法**:
- 各内部クラスを用いて実際にBacklogと通信するか、モッククラスを使用
- サービスレイヤーとインフラストラクチャレイヤーの連携をテスト
- リポジトリパターンの実装が正しく機能することを確認
- 実際のデータベースやAPIとの連携をテスト（または適切にモック化）

**ディレクトリ**: `tests/integration/`

**実行コマンド**: `pytest tests/integration/`

## 3. E2Eテスト (End-to-End Test)

**目的**: システム全体が実際の環境に近い状態で正しく動作することを確認する。

**実施方法**:
- Docker Composeを使用してFastAPIサーバーをコンテナ上でホスト
- HTTPリクエストを送信してAPIエンドポイントをテスト
- MCPプロトコルを使用してBacklogを操作
- 実際のユーザーシナリオに基づいたテストケースを作成
- FastAPIのテストクライアントではなく、実際のHTTPクライアントを使用

**ディレクトリ**: `tests/e2e/`

**実行コマンド**: `bash scripts/run_docker_e2e_tests.sh`

## 3.1. 同期E2Eテスト (Synchronous E2E Test)

**目的**: 同期的なAPIエンドポイントが正しく動作することを確認する。

**実施方法**:
- Docker Composeを使用してFastAPIサーバーをコンテナ上でホスト
- 同期的なHTTPリクエストを送信してAPIエンドポイントをテスト
- 実際のユーザーシナリオに基づいたテストケースを作成
- テスト結果をコンソールに出力

**ディレクトリ**: `tests/e2e/`

**実行コマンド**: `bash scripts/run_sync_e2e_test.sh`

**詳細ドキュメント**: `docs/SYNC_E2E_TESTING.md`

## 3.2. MCP Inspector E2Eテスト (MCP Inspector E2E Test)

**目的**: MCPサーバーがMCP Inspectorを使用して正しく動作することを確認する。

**実施方法**:
- Docker Composeを使用してFastAPIサーバーをコンテナ上でホスト
- MCP Inspectorを使用してMCPサーバーをテスト
- 利用可能なツールとリソースをテスト
- テスト結果をJSON形式で保存し、HTMLレポートを生成

**ディレクトリ**: `tests/e2e/`

**実行コマンド**: 
```bash
# 単一テストの実行
bash scripts/run_inspector_e2e_test.sh [テストメソッド]

# テストスイートの実行
bash scripts/run_inspector_test_suite.sh
```

**テストケース定義**: `tests/e2e/mcp_inspector_test_cases.json`

**レポート生成**: `scripts/generate_inspector_report.py`

**詳細ドキュメント**: `docs/MCP_INSPECTOR_TESTING.md`

## 4. デプロイテスト (Deployment Test)

**目的**: コンテナ化された環境でシステムが正しく動作することを確認する。

**実施方法**:
- Dockerfileとdocker-compose.ymlを使用してFastAPIをコンテナ化
- コンテナ化された環境でE2Eテストを実行（E2Eテストと統合）
- 複数のサービスが連携する場合は、それらの連携もテスト
- 環境変数や設定ファイルが正しく読み込まれることを確認

**実行コマンド**: 
```bash
bash scripts/run_docker_e2e_tests.sh
```

## 5. CIテスト (Continuous Integration Test)

**目的**: コードの変更がマージされる前に、自動的にテストを実行して品質を確保する。

**実施方法**:
- GitHub Actionsを使用して自動テストを実行
- Unitテストと結合テスト（モック使用）を実行
- コードカバレッジを測定し、閾値を下回る場合はビルドを失敗させる
- コードスタイルチェックやセキュリティスキャンも実施

**設定ファイル**: `.github/workflows/ci.yml`

**実行タイミング**: プルリクエスト作成時、マージ時

## 6. CDテスト (Continuous Deployment Test)

**目的**: デプロイされた環境が正しく動作することを確認する。

**実施方法**:
- CDKで環境をデプロイ
- デプロイされたCloudfront/API Gateway/Lambdaに対するAPIリクエストを行うE2Eテスト用Lambdaもデプロイ
- このLambdaを手動実行してテストを実施
- 本番環境に近いステージング環境でテストを実施

**ディレクトリ**: `cdk/test/`

**実行方法**: AWS Management ConsoleまたはAWS CLIからLambda関数を実行

## テスト実施のルール

1. **テストファースト**: すべての新規機能・修正はテストファースト（テスト→実装→リファクタ）で行うこと
2. **テストなき実装の禁止**: テストなき実装ファイルのコミットはCIで警告
3. **自動テスト**: pytestによる自動テスト・カバレッジ計測をCIで必須化
4. **テスト粒度**: テストはunit/integration/e2eに分類し、各粒度で必ずテストを作成
5. **APIテスト**: FastAPIエンドポイントも必ずテストを作成
6. **テストと実装の管理**: テストコードと実装コードは常にペアで管理すること

## テスト失敗時の対応ルール

テストで失敗が発生した場合、テストをスキップ（skip）したり、passやassert True等で無意味に通過させるのではなく、テストの意義を確認し、必要に応じて実装やテスト自体を修正し、正しくテストが通る状態にすること。

## MCPサーバーテストのルール

1. MCPサーバーのテストはスキップせず、通るように実装を修正すること
2. MCPサーバーとの通信にはMCP Clientを使用すること（referenceディレクトリに参考SDKあり）
3. E2Eテストでは、Docker環境で起動したFastAPIサーバーに対してHTTPリクエストを送信してテストすること
