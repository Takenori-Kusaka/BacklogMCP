o#!/bin/bash
# MCP Inspectorテストスイート実行スクリプト

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

# テストケースJSONファイルのパス
TEST_CASES_FILE="tests/e2e/mcp_inspector_test_cases.json"

# テスト結果を保存するディレクトリ
REPORT_DIR="test-reports/mcp-inspector"
mkdir -p $REPORT_DIR

# タイムスタンプ
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SUMMARY_FILE="$REPORT_DIR/suite_summary_${TIMESTAMP}.json"
SUMMARY_TXT="$REPORT_DIR/suite_summary_${TIMESTAMP}.txt"

# 認証情報の確認
HAS_AUTH=false
if [ -n "$BACKLOG_API_KEY" ] && [ -n "$BACKLOG_SPACE" ] && [ -n "$BACKLOG_PROJECT" ]; then
    HAS_AUTH=true
    echo "認証情報が設定されています。認証が必要なテストも実行します。"
else
    echo "警告: 認証情報が設定されていません。認証が必要なテストはスキップされます。"
    echo "認証情報を設定するには、以下の環境変数を設定してください："
    echo "  BACKLOG_API_KEY: Backlog APIキー"
    echo "  BACKLOG_SPACE: Backlogスペース名"
    echo "  BACKLOG_PROJECT: Backlogプロジェクトキー"
fi

# 課題キーの確認
HAS_ISSUE=false
if [ -n "$BACKLOG_ISSUE" ]; then
    HAS_ISSUE=true
    echo "課題キーが設定されています。課題が必要なテストも実行します。"
else
    echo "警告: 課題キーが設定されていません。課題が必要なテストはスキップされます。"
    echo "課題キーを設定するには、BACKLOG_ISSUE環境変数を設定してください。"
fi

# テストケースJSONファイルの存在確認
if [ ! -f "$TEST_CASES_FILE" ]; then
    echo "エラー: テストケースファイル $TEST_CASES_FILE が見つかりません。"
    exit 1
fi

# jqコマンドの存在確認
if ! command -v jq &> /dev/null; then
    echo "警告: jqコマンドがインストールされていません。"
    echo "テストケースの解析に問題が発生する可能性があります。"
    echo "jqをインストールすることをお勧めします: https://stedolan.github.io/jq/download/"
    # jqがない場合は、簡易的な解析を行う
    BASIC_TESTS=$(grep -o '"method": "[^"]*"' "$TEST_CASES_FILE" | grep -o '"[^"]*"$' | tr -d '"')
else
    # jqを使用してテストケースを抽出
    BASIC_TESTS=$(jq -r '.basic_tests[].method' "$TEST_CASES_FILE")
    TOOL_TESTS=$(jq -r '.tool_tests[] | select(.requires_auth == true) | .method' "$TEST_CASES_FILE")
    RESOURCE_TESTS=$(jq -r '.resource_tests[] | select(.requires_auth == true) | .method' "$TEST_CASES_FILE")
    ERROR_TESTS=$(jq -r '.error_tests[].method' "$TEST_CASES_FILE")
    
    # 課題が必要なテストを抽出
    ISSUE_TESTS=$(jq -r '.resource_tests[] | select(.requires_issue == true) | .method' "$TEST_CASES_FILE")
fi

# プロジェクト名の設定（環境変数から取得、または現在時刻を使用）
PROJECT_NAME=${PROJECT_NAME:-"backlog-mcp-suite-$(date +%s)"}

# ポートの設定（環境変数から取得、またはデフォルト値を使用）
PORT=${PORT:-8000}

# Docker Composeを使用してBacklogMCPサーバーを起動
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
MAX_RETRIES=10
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

# テスト結果の初期化
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# テスト結果の配列を初期化
TEST_RESULTS=()

# テスト実行関数
run_test() {
    local test_name="$1"
    local test_method="$2"
    local expected_error="${3:-false}"
    
    echo "----------------------------------------"
    echo "テスト実行: $test_name"
    echo "コマンド: $test_method"
    echo "----------------------------------------"
    
    # テスト結果ファイル
    local test_report="$REPORT_DIR/report_${test_name// /_}_${TIMESTAMP}.json"
    local test_log="$REPORT_DIR/log_${test_name// /_}_${TIMESTAMP}.txt"
    
    # テストを実行
    npx @modelcontextprotocol/inspector $SERVER_URL/mcp --headless --transport streamable-http --output-format json --method "$test_method" > "$test_report" 2> "$test_log"
    local test_result=$?
    
    # 期待されるエラーの場合は、エラーが発生したら成功とみなす
    if [ "$expected_error" = "true" ]; then
        if [ $test_result -ne 0 ]; then
            test_result=0
            echo "期待されるエラーが発生しました。テストは成功です。"
        else
            test_result=1
            echo "エラーが発生しませんでした。テストは失敗です。"
        fi
    fi
    
    # テスト結果を表示
    if [ $test_result -eq 0 ]; then
        echo "テスト結果: 成功 ✅"
        PASSED_TESTS=$((PASSED_TESTS+1))
        TEST_RESULTS+=("{\"name\":\"$test_name\",\"method\":\"$test_method\",\"status\":\"success\",\"report\":\"$test_report\",\"log\":\"$test_log\"}")
    else
        echo "テスト結果: 失敗 ❌"
        echo "エラーログ:"
        cat "$test_log"
        FAILED_TESTS=$((FAILED_TESTS+1))
        TEST_RESULTS+=("{\"name\":\"$test_name\",\"method\":\"$test_method\",\"status\":\"failure\",\"report\":\"$test_report\",\"log\":\"$test_log\"}")
    fi
    
    TOTAL_TESTS=$((TOTAL_TESTS+1))
    echo "----------------------------------------"
}

# 基本テストの実行
echo "========================================================="
echo "基本テストを実行します..."
echo "========================================================="

if [ -n "$BASIC_TESTS" ]; then
    while IFS= read -r test_method; do
        if [ -n "$test_method" ]; then
            # jqがある場合は、テスト名を取得
            if command -v jq &> /dev/null; then
                test_name=$(jq -r ".basic_tests[] | select(.method == \"$test_method\") | .name" "$TEST_CASES_FILE")
            else
                test_name="基本テスト: $test_method"
            fi
            run_test "$test_name" "$test_method"
        fi
    done <<< "$BASIC_TESTS"
else
    echo "基本テストがありません。"
fi

# 認証が必要なテストの実行
if [ "$HAS_AUTH" = "true" ]; then
    echo "========================================================="
    echo "ツールテストを実行します..."
    echo "========================================================="
    
    if [ -n "$TOOL_TESTS" ]; then
        while IFS= read -r test_method; do
            if [ -n "$test_method" ]; then
                # 環境変数を展開
                expanded_method=$(eval echo "$test_method")
                # jqがある場合は、テスト名を取得
                if command -v jq &> /dev/null; then
                    test_name=$(jq -r ".tool_tests[] | select(.method == \"$test_method\") | .name" "$TEST_CASES_FILE")
                else
                    test_name="ツールテスト: $expanded_method"
                fi
                run_test "$test_name" "$expanded_method"
            fi
        done <<< "$TOOL_TESTS"
    else
        echo "ツールテストがありません。"
    fi
    
    echo "========================================================="
    echo "リソーステストを実行します..."
    echo "========================================================="
    
    if [ -n "$RESOURCE_TESTS" ]; then
        while IFS= read -r test_method; do
            if [ -n "$test_method" ]; then
                # 課題が必要なテストかどうかを確認
                requires_issue=false
                if command -v jq &> /dev/null; then
                    requires_issue=$(jq -r ".resource_tests[] | select(.method == \"$test_method\") | .requires_issue // false" "$TEST_CASES_FILE")
                fi
                
                # 課題が必要なテストで、課題キーが設定されていない場合はスキップ
                if [ "$requires_issue" = "true" ] && [ "$HAS_ISSUE" != "true" ]; then
                    echo "----------------------------------------"
                    echo "テストスキップ: 課題キーが設定されていないため、このテストはスキップされます。"
                    echo "テスト: $test_method"
                    echo "----------------------------------------"
                    SKIPPED_TESTS=$((SKIPPED_TESTS+1))
                    continue
                fi
                
                # 環境変数を展開
                expanded_method=$(eval echo "$test_method")
                # jqがある場合は、テスト名を取得
                if command -v jq &> /dev/null; then
                    test_name=$(jq -r ".resource_tests[] | select(.method == \"$test_method\") | .name" "$TEST_CASES_FILE")
                else
                    test_name="リソーステスト: $expanded_method"
                fi
                run_test "$test_name" "$expanded_method"
            fi
        done <<< "$RESOURCE_TESTS"
    else
        echo "リソーステストがありません。"
    fi
else
    echo "========================================================="
    echo "認証情報が設定されていないため、認証が必要なテストはスキップされます。"
    echo "========================================================="
    
    # 認証が必要なテストの数をカウント
    if command -v jq &> /dev/null; then
        AUTH_TEST_COUNT=$(jq -r '.tool_tests | map(select(.requires_auth == true)) | length + .resource_tests | map(select(.requires_auth == true)) | length' "$TEST_CASES_FILE")
        SKIPPED_TESTS=$((SKIPPED_TESTS+AUTH_TEST_COUNT))
    fi
fi

# エラーテストの実行
echo "========================================================="
echo "エラーテストを実行します..."
echo "========================================================="

if [ -n "$ERROR_TESTS" ]; then
    while IFS= read -r test_method; do
        if [ -n "$test_method" ]; then
            # jqがある場合は、テスト名とエラー期待フラグを取得
            if command -v jq &> /dev/null; then
                test_name=$(jq -r ".error_tests[] | select(.method == \"$test_method\") | .name" "$TEST_CASES_FILE")
                expected_error=$(jq -r ".error_tests[] | select(.method == \"$test_method\") | .expected_error // false" "$TEST_CASES_FILE")
            else
                test_name="エラーテスト: $test_method"
                expected_error="true"
            fi
            run_test "$test_name" "$test_method" "$expected_error"
        fi
    done <<< "$ERROR_TESTS"
else
    echo "エラーテストがありません。"
fi

# テスト結果のサマリーを作成
echo "========================================================="
echo "テスト実行結果"
echo "========================================================="
echo "合計テスト数: $TOTAL_TESTS"
echo "成功: $PASSED_TESTS"
echo "失敗: $FAILED_TESTS"
echo "スキップ: $SKIPPED_TESTS"
echo "========================================================="

# テスト結果のサマリーをJSONで保存
echo "{\"timestamp\":\"$(date -Iseconds)\",\"total\":$TOTAL_TESTS,\"passed\":$PASSED_TESTS,\"failed\":$FAILED_TESTS,\"skipped\":$SKIPPED_TESTS,\"tests\":[${TEST_RESULTS[*]}]}" > "$SUMMARY_FILE"

# テスト結果のサマリーをテキストで保存
{
    echo "MCP Inspectorテスト実行結果"
    echo "実行日時: $(date)"
    echo "----------------------------------------"
    echo "合計テスト数: $TOTAL_TESTS"
    echo "成功: $PASSED_TESTS"
    echo "失敗: $FAILED_TESTS"
    echo "スキップ: $SKIPPED_TESTS"
    echo "----------------------------------------"
    echo "詳細なレポートは $SUMMARY_FILE を参照してください。"
} > "$SUMMARY_TXT"

# HTMLレポートの生成
echo "========================================================="
echo "HTMLレポートを生成しています..."
echo "========================================================="
./scripts/generate_inspector_report.py --report-dir "$REPORT_DIR" --output "$REPORT_DIR/report.html" --title "MCP Inspector テスト結果"

# HTMLレポートのパスを表示
REPORT_HTML="$REPORT_DIR/report.html"
if [ -f "$REPORT_HTML" ]; then
    echo "HTMLレポートが生成されました: $REPORT_HTML"
    echo "以下のコマンドでブラウザで開くことができます:"
    echo "  open $REPORT_HTML  # macOSの場合"
    echo "  xdg-open $REPORT_HTML  # Linuxの場合"
    echo "  start $REPORT_HTML  # Windowsの場合"
fi

# テスト結果に基づいて終了コードを設定
if [ $FAILED_TESTS -gt 0 ]; then
    echo "テストに失敗があります。詳細は $SUMMARY_TXT または $REPORT_HTML を参照してください。"
    exit 1
else
    echo "すべてのテストが成功しました。"
    exit 0
fi
