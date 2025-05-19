# Docker環境でのE2Eテスト実行ガイド

このドキュメントでは、Docker環境を使用してBacklogMCPのE2Eテストを実行する方法について説明します。**従来のサブプロセスでFastAPIをホスティングする方法は廃止され、現在はDocker Composeを使用した方法のみがサポートされています。**

## 前提条件

以下のソフトウェアがインストールされていることを確認してください：

1. Docker
2. Docker Compose
3. Poetry（Pythonパッケージ管理）
4. Bash（シェルスクリプト実行用）

## Docker環境でのE2Eテスト実行手順

### 1. 環境変数の設定

以下の環境変数を設定します。これらはDockerコンテナ内のBacklogMCPサーバーで使用されます：

```bash
export BACKLOG_API_KEY=あなたのBacklog APIキー
export BACKLOG_SPACE=あなたのBacklogスペース名
export BACKLOG_PROJECT=テスト対象のプロジェクトキー
export BACKLOG_DISABLE_SSL_VERIFY=false  # 必要に応じてtrueに設定
```

### 2. Dockerを使用したE2Eテスト実行

プロジェクトのルートディレクトリで以下のコマンドを実行します：

```bash
bash scripts/run_docker_e2e_tests.sh
```

このスクリプトは以下の処理を行います：

1. Docker Composeを使用してBacklogMCPサーバーをビルドして起動
2. サーバーが正常に起動するのを待機
3. E2Eテストを実行
4. テスト完了後にDockerコンテナを停止

### 3. 個別のテストファイルを実行する場合

特定のテストファイルだけを実行したい場合は、以下のようにします：

```bash
# Docker環境でサーバーを起動
docker-compose -f docker/docker-compose.yml up -d --build

# サーバーのURLを環境変数に設定
export DOCKER_MCP_SERVER_URL=http://localhost:8000

# 特定のテストファイルを実行
poetry run pytest tests/e2e/test_issue_e2e.py -v

# 終了後にDockerコンテナを停止
docker-compose -f docker/docker-compose.yml down
```

## トラブルシューティング

### サーバー起動の問題

サーバーの起動に問題がある場合は、以下のコマンドでログを確認できます：

```bash
docker-compose -f docker/docker-compose.yml logs
```

### テストの失敗

テストが失敗した場合は、以下を確認してください：

1. 環境変数が正しく設定されているか
2. BacklogのAPIキーが有効か
3. 指定したプロジェクトが存在し、アクセス権があるか

### Dockerコンテナの手動クリーンアップ

問題が発生した場合、以下のコマンドでコンテナを強制的に停止できます：

```bash
docker-compose -f docker/docker-compose.yml down --remove-orphans
```

## メリット

1. **安定性の向上**: サブプロセスでのFastAPI起動に比べて安定性が向上
2. **環境の一貫性**: すべての開発者が同じDocker環境でテストを実行できる
3. **CI/CD統合の容易さ**: CI/CD環境で同じDockerコンテナを使用できる
4. **クリーンな環境**: 毎回新しいコンテナでテストを実行するため、前回のテストの影響を受けない

## 注意点

- E2Eテストには有効なBacklog APIキーが必要です
- Dockerを使用するため、初回実行時はイメージのビルドに時間がかかります
