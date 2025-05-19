#!/bin/bash
# 同期的なE2Eテストを実行するためのスクリプト
# 特定のテストファイルまたはテスト関数を指定して実行できます

set -e  # エラーが発生したら即座に終了

# スクリプトのディレクトリに移動
cd "$(dirname "$0")/.."

# .envファイルが存在すれば読み込む
if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo ".envファイルを読み込みました。"
else
    echo "警告: .envファイルが見つかりません。"
fi

# 引数の確認
if [ $# -eq 0 ]; then
    echo "実行するE2Eテストファイルが指定されていません。"
    echo "テストを実行するには、引数にテストファイルのパスを指定してください。"
    echo "例: bash scripts/run_sync_e2e_test.sh tests/e2e/your_new_test_file.py"
    exit 0 # 何も実行せずに正常終了
fi

# 引数がある場合は、指定されたテストを実行
TEST_PATH="$1"
echo "指定されたテストを実行します: $TEST_PATH"

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
# ネットワークのラベル不整合エラーを回避するため、ネットワークも明示的に削除
docker network rm backlog-mcp-test_default || true
docker-compose -f docker/docker-compose.test.yml down --remove-orphans
# 万が一downで消えなくても強制的に削除
docker rm -f backlog-mcp-api-test || true
docker-compose -f docker/docker-compose.test.yml up -d --build

# サーバーの起動を待つ
echo "サーバーの起動を待っています..."
MAX_RETRIES=10  # 最大リトライ回数を10回（10秒）に短縮
RETRY_COUNT=0
SERVER_URL="http://localhost:8001"

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

echo "DEBUG: TEST_TYPE の値を確認: [$TEST_TYPE]" # デバッグ用に追加

if [ "$TEST_TYPE" == "openapi" ]; then
    echo "========================================================="
    echo "OpenAPIベースのE2Eテスト (Schemathesis) を実行します..."
    echo "========================================================="

    echo "OpenAPI仕様書を生成します..."
    poetry run python3 scripts/generate_openapi.py
    if [ $? -ne 0 ]; then
        echo "エラー: OpenAPI仕様書の生成に失敗しました。"
        docker-compose -f docker/docker-compose.test.yml down
        exit 1
    fi
    echo "OpenAPI仕様書 (docs/openapi.yaml) が生成されました。"

    echo "Schemathesisを実行します..."
    # APIキーが必要な場合は、環境変数 BACKLOG_API_KEY をここで設定するか、
    # Schemathesisのフック機能でリクエストヘッダーに追加する必要があります。
    # 例: poetry run st run docs/openapi.yaml --base-url "$SERVER_URL" --header "X-API-KEY:$BACKLOG_API_KEY"
    # 今回はまずAPIキーなしで実行できる範囲で試します。
    # また、Schemathesisの出力が詳細になるように -v オプションや、
    # 失敗時に詳細な情報を表示する --show-errors-tracebacks をつけるとデバッグに役立ちます。
    # 状態を変えるテスト（POST, PUT, DELETEなど）は --hypothesis-phases=explicit のように実行を制御できます。
    # 今回は基本的な実行のみ試します。
    poetry run st run docs/openapi.yaml --base-url "$SERVER_URL" --validate-schema=false -c all --hypothesis-max-examples=10
    TEST_RESULT=$?
else
    echo "エラー: 不明なテスト種別が指定されました: $SCRIPT_INTERNAL_TEST_TYPE"
    echo "利用可能なテスト種別: openapi"
    echo "例: bash scripts/run_sync_e2e_test.sh openapi"
    TEST_RESULT=1
fi

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
