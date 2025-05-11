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

# AWS_SESSION_TOKEN はオプションなので、.env になくても問題ない
# ただし、.env に空で定義されている場合 (AWS_SESSION_TOKEN=) は -z で検知できないため、
# 明示的に入力が必要かどうかを尋ねるか、挙動をユーザーに委ねるか検討が必要。
# ここでは、.env に設定されていなければ尋ねる形を維持します。
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

# CDK環境変数の確認
echo "CDK環境変数を確認しています..."
echo "CDK_DEFAULT_ACCOUNT: $CDK_DEFAULT_ACCOUNT"
echo "CDK_DEFAULT_REGION: $CDK_DEFAULT_REGION"
echo "AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION"

# CDKのバージョン確認
echo "CDKのバージョンを確認しています..."
npx cdk --version

# デプロイ前のスタック一覧を表示
echo "デプロイ前のスタック一覧を表示します..."
STACKS=$(npx cdk list)
echo "検出されたスタック: $STACKS"

if [ -z "$STACKS" ]; then
    echo "警告: スタックが見つかりません。CDKアプリケーションが正しく設定されているか確認してください。"
    echo "CDKアプリケーションの詳細情報を表示します..."
    npx cdk context
    npx cdk doctor
fi

# CDKのシンセサイズ
echo "CDKをシンセサイズしています..."
npx cdk synth > cdk.out.yaml
echo "シンセサイズ結果のサマリー:"
grep "Resources:" cdk.out.yaml -A 10 || echo "リソースセクションが見つかりません"
rm cdk.out.yaml

# ログファイル名にタイムスタンプを含める
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_DIR="../logs"
DEPLOY_LOG_FILE="${LOG_DIR}/cdk_deploy_${TIMESTAMP}.log"

# ログディレクトリの存在確認と作成
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
    echo "ログディレクトリを作成しました: $LOG_DIR"
fi

# CDKのデプロイ
echo "CDKをデプロイしています..."
echo "ログは ${DEPLOY_LOG_FILE} に出力されます"
export CDK_DEBUG=true
npx cdk deploy --all --require-approval never --verbose --debug > "${DEPLOY_LOG_FILE}" 2>&1

DEPLOY_RESULT=$?
if [ $DEPLOY_RESULT -ne 0 ]; then
    echo "CDKのデプロイに失敗しました。終了コード: $DEPLOY_RESULT"
    echo "詳細なログは ${DEPLOY_LOG_FILE} を確認してください"
    echo "CDKのデバッグ情報を表示します..."
    npx cdk doctor
    
    # ログファイルの最後の数行を表示（エラーメッセージを確認するため）
    echo "ログファイルの最後の20行:"
    tail -n 20 "${DEPLOY_LOG_FILE}"
    
    exit 1
else
    echo "CDKのデプロイが完了しました。詳細なログは ${DEPLOY_LOG_FILE} を確認してください"
    
    # ログファイルからデプロイの概要を抽出して表示
    echo "デプロイの概要:"
    grep -A 10 "Stack ARN" "${DEPLOY_LOG_FILE}" || echo "デプロイの概要が見つかりません"
    
    # デプロイ後のスタック一覧を表示
    echo "デプロイ後のスタック一覧を表示します..."
    STACKS_AFTER=$(npx cdk list)
    echo "検出されたスタック: $STACKS_AFTER"
    
    # CloudFormationスタックの確認
    echo "CloudFormationスタックを確認しています..."
    aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE
fi
