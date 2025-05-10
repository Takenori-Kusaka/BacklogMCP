#!/bin/bash

# AWS認証情報を入力
echo "AWSアクセスキーIDを入力してください:"
read AWS_ACCESS_KEY_ID

echo "AWSシークレットアクセスキーを入力してください:"
read -s AWS_SECRET_ACCESS_KEY
echo ""

echo "AWSセッショントークンを入力してください (必要な場合、不要な場合は空欄):"
read -s AWS_SESSION_TOKEN
echo ""

echo "AWSリージョンを入力してください (デフォルト: us-east-1):"
read AWS_DEFAULT_REGION
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}

# 環境変数をエクスポート
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

# CDKディレクトリに移動
cd cdk

# CDKのビルド
echo "CDKをビルドしています..."
npm run build

if [ $? -ne 0 ]; then
    echo "CDKのビルドに失敗しました。"
    exit 1
fi

# CDKのシンセサイズ
echo "CDKをシンセサイズしています..."
npx cdk synth --context environment=dev

if [ $? -ne 0 ]; then
    echo "CDKのシンセサイズに失敗しました。"
    exit 1
fi

# スタック一覧を表示
echo "スタック一覧を表示します..."
npx cdk list --context environment=dev

# CDKのドライラン
echo "CDKのドライランを実行しています..."
npx cdk deploy --all --dry-run --no-validate --context environment=dev --verbose

if [ $? -ne 0 ]; then
    echo "CDKのドライランに失敗しました。"
    exit 1
else
    echo "CDKのドライランが完了しました。"
fi
