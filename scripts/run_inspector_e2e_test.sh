#!/bin/bash
# MCP Inspectorを使用したE2Eテスト実行スクリプト

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
    # 引数がない場合は、デフォルトのテストを実行
    TEST_METHOD="tools/list"
    echo "デフォルトのテストを実行します: $TEST_METHOD"
else
    # 引数がある場合は、指定されたテストを実行
    TEST_METHOD="$1"
    echo "指定されたテストを実行します: $TEST_METHOD"
fi

# Node.jsがインストールされているか確認
if ! command -v node &> /dev/null; then
    echo "エラー: Node.jsがインストールされていません。"
    echo "Node.jsをインストールしてから再実行してください。"
    exit 1
fi

# MCP Inspectorがインストールされているか確認
if ! npm list -g @modelcontextprotocol/inspector &> /dev/null && ! npm list @modelcontextprotocol/inspector &> /dev/null; then
    echo "MCP Inspectorがインストールされていません。インストールを試みます..."
    npm install -g @modelcontextprotocol/inspector
    if [ $? -ne 0 ]; then
        echo "エラー: MCP Inspectorのインストールに失敗しました。"
        echo "手動でインストールしてください: npm install -g @modelcontextprotocol/inspector"
        exit 1
    fi
    echo "MCP Inspectorをインストールしました。"
fi

# Poetryがインストールされているか確認
if ! command -v poetry &> /dev/null; then
    echo "エラー: poetryがインストールされていません。"
    echo "poetryをインストールしてから再実行してください。"
    echo "インストール方法: https://python-poetry.org/docs/#installation"
    exit 1
fi

echo "========================================================="
echo "MCP Inspectorを使用してBacklogMCPサーバーをテストします..."
echo "========================================================="

# Poetry依存関係が正しくインストールされているか確認
echo "Poetry依存関係を確認しています..."
poetry install --no-interaction

# テスト実行前に必要な環境変数を設定
export PYTHONUNBUFFERED=1  # Pythonの出力バッファリングを無効化

# Docker Composeを使用してBacklogMCPサーバーを起動
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

# MCP Inspectorを使用してテスト実行
echo "========================================================="
echo "MCP Inspector CLIモードでテストを実行: $TEST_METHOD"
echo "========================================================="

# テスト結果を保存するディレクトリ
REPORT_DIR="test-reports/mcp-inspector"
mkdir -p $REPORT_DIR

# タイムスタンプ付きのレポートファイル名
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="$REPORT_DIR/report_${TIMESTAMP}.json"
LOG_FILE="$REPORT_DIR/log_${TIMESTAMP}.txt"

echo "========================================================="
echo "MCP Inspectorテストを実行中..."
echo "テストメソッド: $TEST_METHOD"
echo "レポートファイル: $REPORT_FILE"
echo "ログファイル: $LOG_FILE"
echo "========================================================="

# ヘッドレスモードで実行し、結果をJSONとして保存
npx @modelcontextprotocol/inspector $SERVER_URL/mcp --headless --transport streamable-http --output-format json > $REPORT_FILE 2> $LOG_FILE

# テスト実行の結果を保存
TEST_RESULT=$?

# テスト結果の概要を表示
if [ $TEST_RESULT -eq 0 ]; then
    echo "========================================================="
    echo "テストが正常に完了しました。"
    
    # JSONからテスト結果の概要を抽出して表示
    if [ -f $REPORT_FILE ]; then
        echo "テスト結果の概要:"
        echo "----------------------------------------"
        # jqがインストールされている場合はJSONを整形して表示
        if command -v jq &> /dev/null; then
            jq '.results | "成功: \(.success) / 失敗: \(.failure) / 合計: \(.total)"' $REPORT_FILE -r || cat $REPORT_FILE | head -20
        else
            # jqがない場合は簡易的な表示
            grep -E '"success"|"failure"|"total"' $REPORT_FILE || cat $REPORT_FILE | head -20
        fi
        echo "----------------------------------------"
        echo "詳細なレポートは $REPORT_FILE を参照してください。"
    fi
    echo "========================================================="
else
    echo "========================================================="
    echo "テストが失敗しました。終了コード: $TEST_RESULT"
    echo "エラーログ:"
    echo "----------------------------------------"
    cat $LOG_FILE
    echo "----------------------------------------"
    echo "詳細なレポートは $REPORT_FILE を参照してください。"
    echo "========================================================="
fi

# テスト結果のサマリーをJSONで作成
SUMMARY_FILE="$REPORT_DIR/summary.json"
echo "{\"timestamp\":\"$(date -Iseconds)\",\"method\":\"$TEST_METHOD\",\"status\":\"$([ $TEST_RESULT -eq 0 ] && echo 'success' || echo 'failure')\",\"report\":\"$REPORT_FILE\",\"log\":\"$LOG_FILE\"}" > $SUMMARY_FILE

exit $TEST_RESULT
