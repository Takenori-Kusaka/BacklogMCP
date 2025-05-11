#!/bin/bash

# .envファイルが存在すれば読み込む
if [ -f ".env" ]; then
  echo ".envファイルを読み込みます..."
  # コメント行と空行を除外し、各行を export
  # IFS= を設定して、行頭・行末の空白を保持しつつ、= の前後での分割を防ぐ
  # -r オプションでバックスラッシュによるエスケープを無効にする
  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" =~ ^\s*# ]] || [[ "$line" =~ ^\s*$ ]]; then
      continue # コメント行と空行をスキップ
    fi
    # KEY=VALUE の形式であることを期待し、そのまま export
    # これにより、VALUE に含まれる特殊文字も比較的安全に扱える
    export "$line"
  done < <(grep -v '^#' .env | grep -v '^$' | tr -d '\r') # プロセス置換で grep 結果を渡し、\r を除去
fi

# AWS認証情報を入力 (環境変数に設定されていない場合)
if [ -z "$AWS_ACCESS_KEY_ID" ]; then
  echo "AWSアクセスキーIDを入力してください:"
  read AWS_ACCESS_KEY_ID
fi

if [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
  echo "AWSシークレットアクセスキーを入力してください:"
  read -s AWS_SECRET_ACCESS_KEY
  echo ""
fi

if [ -z "$AWS_SESSION_TOKEN" ]; then
  echo "AWSセッショントークンを入力してください (必要な場合、不要な場合は空欄):"
  read -s AWS_SESSION_TOKEN
  echo ""
fi

if [ -z "$AWS_DEFAULT_REGION" ]; then
  echo "AWSリージョンを入力してください (デフォルト: us-east-1):"
  read AWS_DEFAULT_REGION
fi
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}

# 環境変数をエクスポート (既に .env から export されているものもあるが、readで入力された場合のため)
export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export AWS_SESSION_TOKEN
export AWS_DEFAULT_REGION

# 認証情報が正しく設定されているか確認
echo "AWS認証情報を確認しています..."
aws sts get-caller-identity

if [ $? -ne 0 ]; then
    echo "AWS認証情報の確認に失敗しました。入力した認証情報を確認してください。"
    exit 1
fi

# CDK環境変数を設定
echo "CDK環境変数を設定しています..."
export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
export CDK_DEFAULT_REGION=$AWS_DEFAULT_REGION

echo "CDK環境変数を設定しました:"
echo "CDK_DEFAULT_ACCOUNT=$CDK_DEFAULT_ACCOUNT"
echo "CDK_DEFAULT_REGION=$CDK_DEFAULT_REGION"

# CDKディレクトリに移動
cd cdk

# CDKのビルド
echo "CDKをビルドしています..."
npm run build

if [ $? -ne 0 ]; then
    echo "CDKのビルドに失敗しました。"
    exit 1
fi

# CDKのキャッシュディレクトリをクリア
echo "CDKのキャッシュディレクトリをクリアしています..."
rm -rf cdk.out

# 特定スタックの詳細なシンセサイズログを取得
echo "特定のスタック (BacklogMcpStack-dev) の詳細なシンセサイズログを取得しています..."
# スタック名は環境に合わせて適宜変更してください (例: BacklogMcpStack-stg)
# --context environment=dev は cdk.json の app コマンド経由で渡される想定だが、明示的に指定
npx cdk synth "BacklogMcpStack-dev" --context environment=dev --verbose > cdk-synth-verbose-specific.log 2>&1
if [ $? -ne 0 ]; then
    echo "特定のスタックのシンセサイズに失敗しました。詳細は cdk-synth-verbose-specific.log を確認してください。"
    cat cdk-synth-verbose-specific.log
    # exit 1 # ここで終了させずに、後続の処理も試みる場合はコメントアウト
else
    echo "特定のスタックのシンセサイズログを cdk-synth-verbose-specific.log に保存しました。"
fi

# 少し待機して、前のコマンドが完全に終了するのを待つ
sleep 3

# CDKのシンセサイズ
echo "CDKをシンセサイズしています..."
npx cdk synth --context environment=dev

if [ $? -ne 0 ]; then
    echo "CDKのシンセサイズに失敗しました。"
    exit 1
fi

# 少し待機して、前のコマンドが完全に終了するのを待つ
sleep 3

# CDK環境変数の確認
echo "CDK環境変数を確認しています..."
echo "CDK_DEFAULT_ACCOUNT: $CDK_DEFAULT_ACCOUNT"
echo "CDK_DEFAULT_REGION: $CDK_DEFAULT_REGION"
echo "AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION"

# CDKのバージョン確認
echo "CDKのバージョンを確認しています..."
npx cdk --version

# スタック一覧を表示
echo "スタック一覧を表示します..."
STACKS=$(npx cdk list --context environment=dev)
echo "検出されたスタック: $STACKS"

if [ -z "$STACKS" ]; then
    echo "警告: スタックが見つかりません。CDKアプリケーションが正しく設定されているか確認してください。"
    echo "CDKアプリケーションの詳細情報を表示します..."
    npx cdk context --context environment=dev
    npx cdk doctor
fi

# CDKのシンセサイズ
echo "CDKをシンセサイズしています..."
npx cdk synth --context environment=dev > cdk.out.yaml
echo "シンセサイズ結果のサマリー:"
grep "Resources:" cdk.out.yaml -A 10 || echo "リソースセクションが見つかりません"
rm cdk.out.yaml

# ログファイル名にタイムスタンプを含める
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="../logs"
DRY_RUN_LOG_FILE="${LOG_DIR}/cdk_dry_run_${TIMESTAMP}.log"

# ログディレクトリの存在確認と作成
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
    echo "ログディレクトリを作成しました: $LOG_DIR"
fi

# CDKのドライラン
echo "CDKのドライランを実行しています..."
echo "ログは ${DRY_RUN_LOG_FILE} に出力されます"
npx cdk deploy --all --dry-run --no-validate --require-approval never --context environment=dev --verbose --debug > "${DRY_RUN_LOG_FILE}" 2>&1

DRYRUN_RESULT=$?
if [ $DRYRUN_RESULT -ne 0 ]; then
    echo "CDKのドライランに失敗しました。終了コード: $DRYRUN_RESULT"
    echo "詳細なログは ${DRY_RUN_LOG_FILE} を確認してください"
    echo "CDKのデバッグ情報を表示します..."
    npx cdk doctor
    
    # ログファイルの最後の数行を表示（エラーメッセージを確認するため）
    echo "ログファイルの最後の20行:"
    tail -n 20 "${DRY_RUN_LOG_FILE}"
    
    exit 1
else
    echo "CDKのドライランが完了しました。詳細なログは ${DRY_RUN_LOG_FILE} を確認してください"
    
    # ログファイルからリソース変更の概要を抽出して表示
    echo "リソース変更の概要:"
    grep -A 10 "Stack ARN" "${DRY_RUN_LOG_FILE}" || echo "リソース変更の概要が見つかりません"
    
    # CloudFormationスタックの確認
    echo "CloudFormationスタックを確認しています..."
    aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE
fi
