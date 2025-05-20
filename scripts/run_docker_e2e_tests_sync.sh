#!/bin/bash
# E2Eテストを実行するためのスクリプト（同期実行版）
# Docker上でBacklogMCPサーバーを起動して、E2Eテストを同期的に実行します

set -e  # エラーが発生したら即座に終了

# スクリプトのディレクトリに移動
cd "$(dirname "$0")/.."

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

# プロジェクト名の設定（環境変数から取得、または現在時刻を使用）
PROJECT_NAME=${PROJECT_NAME:-"docker-e2e-sync-$(date +%s)"}

# ポートの設定（環境変数から取得、またはデフォルト値を使用）
PORT=${PORT:-8001}

echo "========================================================="
echo "Docker Composeを使用してBacklogMCPサーバーを起動します..."
echo "プロジェクト名: $PROJECT_NAME"
echo "ポート: $PORT"
echo "========================================================="

# 既存のコンテナを停止・削除してから起動
# プロジェクト名を指定してDocker Composeを実行
docker-compose -f docker/docker-compose.yml -p $PROJECT_NAME down --remove-orphans

# 環境変数を設定してDocker Composeを実行
export PORT=$PORT
docker-compose -f docker/docker-compose.yml -p $PROJECT_NAME up -d --build

# サーバーの起動を待つ
echo "サーバーの起動を待っています..."
MAX_RETRIES=10  # 最大リトライ回数を10回（10秒）に短縮
RETRY_COUNT=0
SERVER_URL="http://localhost:$PORT"

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
    docker-compose -f docker/docker-compose.yml -p $PROJECT_NAME logs
    echo "========================================================="
    echo "コンテナの状態を表示します:"
    echo "========================================================="
    docker ps -a
    docker-compose -f docker/docker-compose.yml -p $PROJECT_NAME down
    exit 1
fi

# Poetry依存関係が正しくインストールされているか確認
echo "Poetry依存関係を確認しています..."
poetry install --no-interaction

# テスト実行前に必要な環境変数を設定
export DOCKER_MCP_SERVER_URL=$SERVER_URL
export PYTHONUNBUFFERED=1  # Pythonの出力バッファリングを無効化

# E2Eテストを実行（-v: 詳細出力、-s: 標準出力をキャプチャしない）
echo "========================================================="
echo "E2Eテストを実行します..."
echo "========================================================="

# 同期的に一つずつテストを実行するために-xvs オプションを使用
# -x: 最初の失敗で停止
# -v: 詳細出力
# -s: 標準出力をキャプチャしない（リアルタイム出力）
poetry run pytest tests/e2e/test_*_sync_e2e.py -xvs

# テスト実行の結果を保存
TEST_RESULT=$?

# サーバーログの表示
echo "========================================================="
echo "サーバーログを表示します..."
echo "========================================================="
docker-compose -f docker/docker-compose.yml -p $PROJECT_NAME logs

# Docker Composeでサービスを停止
echo "========================================================="
echo "Docker Composeでサービスを停止します..."
echo "========================================================="
docker-compose -f docker/docker-compose.yml -p $PROJECT_NAME down

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
