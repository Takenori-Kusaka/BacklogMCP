#!/bin/bash
# 特定の同期テストを実行するためのスクリプト
# 使用例:
# ./scripts/run_specific_sync_test.sh test_issue_sync_e2e.py::test_get_issues_from_real_api
# ./scripts/run_specific_sync_test.sh test_project_sync_e2e.py
# ./scripts/run_specific_sync_test.sh test_bulk_operations_sync_e2e.py::test_bulk_update_status_e2e

set -e  # エラーが発生したら即座に終了

# スクリプトのディレクトリに移動
cd "$(dirname "$0")/.."

# 引数の確認
if [ $# -eq 0 ]; then
    echo "エラー: テスト指定が必要です"
    echo "使用例: $0 test_issue_sync_e2e.py::test_get_issues_from_real_api"
    echo "使用例: $0 test_project_sync_e2e.py"
    exit 1
fi

# テスト指定
TEST_SPEC="tests/e2e/$1"
echo "指定されたテスト: $TEST_SPEC"

# Poetryがインストールされているか確認
if ! command -v poetry &> /dev/null; then
    echo "エラー: poetryがインストールされていません。"
    echo "poetryをインストールしてから再実行してください。"
    echo "インストール方法: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Docker Composeがインストールされているか確認
if ! command -v docker-compose &> /dev/null; then
    echo "エラー: docker-composeがインストールされていません。"
    echo "docker-composeをインストールしてから再実行してください。"
    exit 1
fi

echo "========================================================="
echo "Docker Composeを使用してBacklogMCPサーバーを起動します..."
echo "========================================================="

# 既存のコンテナを停止・削除してから起動
docker-compose -f docker/docker-compose.test.yml down
docker-compose -f docker/docker-compose.test.yml up -d --build

# サーバーの起動を待つ
echo "サーバーの起動を待っています..."
MAX_RETRIES=10  # 最大リトライ回数を10回（10秒）に短縮
RETRY_COUNT=0
SERVER_URL="http://localhost:8000"

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s "$SERVER_URL/" > /dev/null; then
        echo "サーバーが起動しました。"
        break
    fi
    echo "サーバー起動待機中... $((RETRY_COUNT+1))/$MAX_RETRIES"
    sleep 1
    RETRY_COUNT=$((RETRY_COUNT+1))
done

if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "========================================================="
    echo "エラー: サーバーの起動がタイムアウトしました。"
    echo "Docker ログを表示します:"
    echo "========================================================="
    docker-compose -f docker/docker-compose.test.yml logs
    echo "========================================================="
    echo "コンテナの状態を表示します:"
    echo "========================================================="
    docker ps -a
    docker-compose -f docker/docker-compose.test.yml down
    exit 1
fi

# Poetry依存関係が正しくインストールされているか確認
echo "Poetry依存関係を確認しています..."
poetry install --no-interaction

# テスト実行前に必要な環境変数を設定
export DOCKER_MCP_SERVER_URL=$SERVER_URL
export PYTHONUNBUFFERED=1  # Pythonの出力バッファリングを無効化

# 指定されたテストを実行
echo "========================================================="
echo "指定された同期テストを実行します: $TEST_SPEC"
echo "========================================================="

# 同期的に一つずつテストを実行するために-xvs オプションを使用
# -x: 最初の失敗で停止
# -v: 詳細出力
# -s: 標準出力をキャプチャしない（リアルタイム出力）
poetry run pytest $TEST_SPEC -xvs

# テスト実行の結果を保存
TEST_RESULT=$?

# Docker Composeでサービスを停止
echo "========================================================="
echo "Docker Composeでサービスを停止します..."
echo "========================================================="
docker-compose -f docker/docker-compose.test.yml down

# テスト結果に基づいて終了コードを設定
if [ $TEST_RESULT -eq 0 ]; then
    echo "========================================================="
    echo "テストが正常に完了しました。"
    echo "========================================================="
else
    echo "========================================================="
    echo "テストが失敗しました。終了コード: $TEST_RESULT"
    echo "========================================================="
fi

exit $TEST_RESULT
