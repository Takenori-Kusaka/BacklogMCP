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

# CDKのシンセサイズ
echo "CDKをシンセサイズしています..."
npx cdk synth --context environment=dev

if [ $? -ne 0 ]; then
    echo "CDKのシンセサイズに失敗しました。"
    exit 1
fi

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

# CDKのドライラン
echo "CDKのドライランを実行しています..."
npx cdk deploy --all --dry-run --no-validate --context environment=dev --verbose --debug

DRYRUN_RESULT=$?
if [ $DRYRUN_RESULT -ne 0 ]; then
    echo "CDKのドライランに失敗しました。終了コード: $DRYRUN_RESULT"
    echo "CDKのデバッグ情報を表示します..."
    npx cdk doctor
    exit 1
else
    echo "CDKのドライランが完了しました。"
    
    # CloudFormationスタックの確認
    echo "CloudFormationスタックを確認しています..."
    aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE
fi
