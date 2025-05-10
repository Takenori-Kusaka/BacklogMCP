#!/bin/bash

# AWS認証情報を使用してAWSアカウントIDとリージョンを取得し、CDK環境変数を設定するスクリプト

# 引数チェック
if [ $# -eq 0 ]; then
    echo "使用方法: source $0 [リージョン]"
    echo "例: source $0 us-east-1"
    echo "注意: このスクリプトはsourceコマンドで実行する必要があります。"
    return 1 2>/dev/null || exit 1
fi

# 引数からリージョンを取得、または引数がない場合はデフォルト値を使用
REGION=${1:-us-east-1}

# AWS CLIがインストールされているか確認
if ! command -v aws &> /dev/null; then
    echo "エラー: AWS CLIがインストールされていません。"
    echo "インストール方法: sudo apt install awscli"
    return 1 2>/dev/null || exit 1
fi

echo "AWS認証情報を確認しています..."
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null)
RESULT=$?

if [ $RESULT -ne 0 ] || [ -z "$ACCOUNT_ID" ]; then
    echo "エラー: AWS認証情報の取得に失敗しました。"
    echo "AWS認証情報が正しく設定されているか確認してください。"
    echo "例:"
    echo "  export AWS_ACCESS_KEY_ID=あなたのアクセスキーID"
    echo "  export AWS_SECRET_ACCESS_KEY=あなたのシークレットアクセスキー"
    echo "  export AWS_SESSION_TOKEN=あなたのセッショントークン（必要な場合）"
    return 1 2>/dev/null || exit 1
fi

# CDK環境変数を設定
export CDK_DEFAULT_ACCOUNT=$ACCOUNT_ID
export CDK_DEFAULT_REGION=$REGION

echo "CDK環境変数を設定しました:"
echo "CDK_DEFAULT_ACCOUNT=$CDK_DEFAULT_ACCOUNT"
echo "CDK_DEFAULT_REGION=$CDK_DEFAULT_REGION"

# 現在のAWS認証情報を表示
echo "現在のAWS認証情報:"
aws sts get-caller-identity

echo ""
echo "注意: このスクリプトはsourceコマンドで実行する必要があります。"
echo "例: source $0 [リージョン]"
