# BacklogMCP CDKデプロイガイド

このガイドでは、AWS CDKを使用したBacklogMCPのデプロイプロセスについて詳細に説明します。デプロイ前のdry run（ドライラン）の実行方法、実際のデプロイ方法、およびトラブルシューティングについて解説します。

## 目次

- [前提条件](#前提条件)
- [環境変数の設定](#環境変数の設定)
- [CDKのドライラン](#cdkのドライラン)
- [CDKのデプロイ](#cdkのデプロイ)
- [ログの確認](#ログの確認)
- [トラブルシューティング](#トラブルシューティング)

## 前提条件

BacklogMCPをAWS CDKでデプロイするには、以下の前提条件が必要です：

- AWS CLIがインストールされていること
- AWS CDKがインストールされていること
- AWSアカウントが設定されていること
- Node.jsがインストールされていること

## 環境変数の設定

BacklogMCPのデプロイには、以下の環境変数が必要です：

```
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_SESSION_TOKEN=your_aws_session_token (必要な場合)
AWS_DEFAULT_REGION=your_aws_region
BACKLOG_API_KEY=your_backlog_api_key
BACKLOG_SPACE=your_backlog_space_name
BACKLOG_PROJECT=your_backlog_project_key
```

これらの環境変数は、`.env`ファイルに設定することができます：

```bash
# .envファイルの例
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1
BACKLOG_API_KEY=your_backlog_api_key
BACKLOG_SPACE=your_backlog_space_name
BACKLOG_PROJECT=your_backlog_project_key
```

## CDKのドライラン

CDKのドライランは、実際のデプロイを行わずに、デプロイによって作成または変更されるリソースを確認するためのプロセスです。これにより、デプロイ前に潜在的な問題を特定し、修正することができます。

### ドライランの実行

ドライランを実行するには、プロジェクトのルートディレクトリで以下のコマンドを実行します：

```bash
./scripts/dry-run-cdk.sh
```

このスクリプトは以下の処理を行います：

1. `.env`ファイルから環境変数を読み込む
2. AWS認証情報を確認する
3. CDK環境変数を設定する
4. CDKをビルドする
5. CDKのキャッシュディレクトリをクリアする（ファイルパスが長すぎるエラーを防止）
6. 特定のスタックの詳細なシンセサイズログを取得する
7. CDKをシンセサイズする
8. CDKのドライランを実行する
9. CloudFormationスタックを確認する

### ログファイル

ドライランの実行中に生成されるログは、以下のファイルに保存されます：

- **特定スタックのシンセサイズログ**: `cdk/cdk-synth-verbose-specific.log`
- **ドライランのログ**: `logs/cdk_dry_run_YYYYMMDD_HHMMSS.log`

ログファイル名にはタイムスタンプが含まれるため、複数回のドライランを実行しても、ログが上書きされることはありません。

### ドライラン結果の確認

ドライランが完了すると、以下の情報が表示されます：

- ドライランの成功または失敗
- ログファイルの場所
- リソース変更の概要（成功した場合）
- エラーメッセージとログファイルの最後の20行（失敗した場合）

ドライランのログファイルを確認して、デプロイによって作成または変更されるリソースを詳細に確認することができます。

## CDKのデプロイ

ドライランで問題がないことを確認したら、実際のデプロイを行うことができます。

### デプロイの実行

デプロイを実行するには、プロジェクトのルートディレクトリで以下のコマンドを実行します：

```bash
./scripts/deploy-cdk.sh
```

このスクリプトは以下の処理を行います：

1. `.env`ファイルから環境変数を読み込む
2. AWS認証情報を確認する
3. CDK環境変数を設定する
4. CDKをビルドする
5. CDKをシンセサイズする
6. CDKをデプロイする
7. デプロイ後のスタック一覧を表示する
8. CloudFormationスタックを確認する

### ログファイル

デプロイの実行中に生成されるログは、以下のファイルに保存されます：

- **デプロイのログ**: `logs/cdk_deploy_YYYYMMDD_HHMMSS.log`

ログファイル名にはタイムスタンプが含まれるため、複数回のデプロイを実行しても、ログが上書きされることはありません。

### デプロイ結果の確認

デプロイが完了すると、以下の情報が表示されます：

- デプロイの成功または失敗
- ログファイルの場所
- デプロイの概要（成功した場合）
- エラーメッセージとログファイルの最後の20行（失敗した場合）
- デプロイ後のスタック一覧
- CloudFormationスタックの状態

デプロイのログファイルを確認して、デプロイの詳細を確認することができます。

## ログの確認

BacklogMCPのCDKデプロイプロセスでは、以下のログファイルが生成されます：

### ドライランのログ

- **ファイル名**: `logs/cdk_dry_run_YYYYMMDD_HHMMSS.log`
- **内容**: CDKのドライラン実行時のログ
- **確認方法**: テキストエディタまたは以下のコマンドで確認できます：

```bash
cat logs/cdk_dry_run_YYYYMMDD_HHMMSS.log
```

特定の情報を検索する場合は、grepコマンドを使用できます：

```bash
# リソース変更の概要を確認
grep -A 10 "Stack ARN" logs/cdk_dry_run_YYYYMMDD_HHMMSS.log

# エラーメッセージを確認
grep "Error" logs/cdk_dry_run_YYYYMMDD_HHMMSS.log
```

### デプロイのログ

- **ファイル名**: `logs/cdk_deploy_YYYYMMDD_HHMMSS.log`
- **内容**: CDKのデプロイ実行時のログ
- **確認方法**: テキストエディタまたは以下のコマンドで確認できます：

```bash
cat logs/cdk_deploy_YYYYMMDD_HHMMSS.log
```

特定の情報を検索する場合は、grepコマンドを使用できます：

```bash
# デプロイの概要を確認
grep -A 10 "Stack ARN" logs/cdk_deploy_YYYYMMDD_HHMMSS.log

# エラーメッセージを確認
grep "Error" logs/cdk_deploy_YYYYMMDD_HHMMSS.log
```

### ログの管理

ログファイルは時間の経過とともに蓄積されるため、定期的に古いログファイルを削除することをお勧めします。以下のコマンドを使用して、30日以上経過したログファイルを削除できます：

```bash
find logs -name "cdk_*.log" -type f -mtime +30 -delete
```

## トラブルシューティング

### よくある問題と解決策

#### 1. AWS認証情報の問題

```
Error: The security token included in the request is invalid
```

**解決策**:
- AWS認証情報が正しく設定されているか確認します。
- AWS CLIの設定を確認します：`aws configure list`
- `.env`ファイルの認証情報を確認します。
- 一時的な認証情報を使用している場合は、有効期限が切れていないか確認します。

#### 2. CDKブートストラップの問題

```
Error: This stack uses assets, so the toolkit stack must be deployed to the environment
```

**解決策**:
- CDKブートストラップを実行します：

```bash
cd cdk
npx cdk bootstrap
```

#### 3. 依存関係の問題

```
Error: Cannot find module '@aws-cdk/aws-lambda'
```

**解決策**:
- 依存関係をインストールします：

```bash
cd cdk
npm install
```

#### 4. スタック名の問題

```
Error: Stack with id BacklogMcpStack-dev does not exist
```

**解決策**:
- スタック名が正しいか確認します。
- 環境変数`environment`が正しく設定されているか確認します。
- `cdk.json`ファイルの設定を確認します。

#### 5. API GatewayのCloudWatch Logsの設定問題

```
Error: CloudWatch Logs role ARN must be set in account settings to enable logging
```

**解決策**:
- `cdk.json`ファイルの`"@aws-cdk/aws-apigateway:disableCloudWatchRole"`設定を`false`に変更します：

```json
{
  "context": {
    "@aws-cdk/aws-apigateway:disableCloudWatchRole": false,
    // 他の設定...
  }
}
```

- この設定により、API GatewayがCloudWatch Logsにログを送信するために必要なロールが自動的に作成されるようになります。

#### 6. ファイルパスが長すぎるエラー

```
Error: ENAMETOOLONG: name too long, copyfile
```

**解決策**:
- CDKのキャッシュディレクトリをクリアします：

```bash
rm -rf cdk/cdk.out
```

- `dry-run-cdk.sh`と`deploy-cdk.sh`スクリプトには、このクリーンアップステップが含まれています。

#### 7. リソース制限の問題

```
Error: The following resource(s) failed to create: [LambdaFunction]
```

**解決策**:
- AWS CloudFormationコンソールでスタックイベントを確認します。
- リソース制限に達していないか確認します。
- ログファイルでエラーの詳細を確認します。

### ログファイルの確認

問題が発生した場合は、ログファイルを確認して詳細なエラーメッセージを確認します：

```bash
# ドライランのログを確認
cat logs/cdk_dry_run_YYYYMMDD_HHMMSS.log | grep "Error"

# デプロイのログを確認
cat logs/cdk_deploy_YYYYMMDD_HHMMSS.log | grep "Error"
```

### CDKのデバッグ情報

CDKのデバッグ情報を表示するには、以下のコマンドを実行します：

```bash
cd cdk
npx cdk doctor
```

### CloudFormationスタックの確認

AWS CloudFormationコンソールでスタックの状態を確認することもできます：

1. AWSマネジメントコンソールにログイン
2. CloudFormationサービスに移動
3. スタック一覧から該当するスタックを選択
4. 「イベント」タブでデプロイイベントを確認
5. 「リソース」タブでリソースの状態を確認

### サポート

問題が解決しない場合は、以下の方法でサポートを受けることができます：

1. GitHubのIssueを作成する
2. プロジェクトのメンテナーに連絡する
3. AWS CDKのドキュメントを参照する: [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/latest/guide/home.html)
