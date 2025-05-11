# BacklogMCP デプロイガイド

このガイドでは、BacklogMCPのデプロイ方法について説明します。AWS CDKを使用したデプロイ、Docker Composeを使用したローカル環境でのデプロイなど、様々なデプロイオプションを提供します。

> **注意**: AWS CDKを使用したデプロイの詳細な手順については、[CDKデプロイガイド](CDK_DEPLOYMENT_GUIDE.md)を参照してください。このガイドには、CDKのドライランとデプロイの詳細な手順、ログファイルの確認方法、およびトラブルシューティングの情報が含まれています。

## 目次

- [AWS CDKによるデプロイ](#aws-cdkによるデプロイ)
- [ローカル環境でのデプロイ](#ローカル環境でのデプロイ)
- [Docker Composeによるデプロイ](#docker-composeによるデプロイ)
- [環境変数の設定](#環境変数の設定)
- [デプロイ後の確認](#デプロイ後の確認)
- [トラブルシューティング](#トラブルシューティング)

## AWS CDKによるデプロイ

BacklogMCPは、AWS CDKを使用してAWS環境にデプロイすることができます。デプロイアーキテクチャは、CloudFront + API Gateway + Lambda（Web Adapter）を使用したFastAPIホスティングアーキテクチャです。

### デプロイアーキテクチャの特徴

- **Lambda Web Adapter**: 既存FastAPIコードの変更不要、ASGI互換性
- **CloudFront**: グローバルキャッシュ、WAF連携、カスタムドメイン管理
- **API Gateway REST**: 使用量プラン管理、APIキー認証、リクエストバリデーション
- **CDK構成**: インフラのコード化、マルチリージョン展開可能性

### 前提条件

- AWS CLIがインストールされていること
- AWS CDKがインストールされていること
- AWSアカウントが設定されていること
- Node.jsがインストールされていること

### デプロイ手順

1. **AWSアカウントの設定**

```bash
aws configure
```

2. **CDKディレクトリに移動**

```bash
cd cdk
```

3. **依存関係のインストール**

```bash
npm install
```

4. **CDKの初期化（初回のみ）**

```bash
cdk bootstrap
```

5. **デプロイの実行**

```bash
./scripts/deploy-cdk.sh
```

または、CDKコマンドを直接実行する場合：

```bash
cdk deploy
```

6. **デプロイの確認**

デプロイが完了すると、以下のような出力が表示されます：

```
Outputs:
BacklogMCPStack.ApiEndpoint = https://xxxxxxxxxx.execute-api.xx-xxxx-x.amazonaws.com/
BacklogMCPStack.CloudFrontDomainName = xxxxxxxxxx.cloudfront.net
```

これらのURLを使用して、APIにアクセスすることができます。

### カスタムドメインの設定

カスタムドメインを使用する場合は、以下の手順で設定します：

1. **Route 53でドメインを設定**

2. **ACMで証明書を発行**

3. **CDKスタックにカスタムドメイン設定を追加**

```typescript
// cdk/lib/backlog-mcp-stack.ts
const domainName = 'api.example.com';
const certificateArn = 'arn:aws:acm:us-east-1:xxxxxxxxxxxx:certificate/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx';

// CloudFrontディストリビューションにカスタムドメイン設定を追加
const distribution = new cloudfront.Distribution(this, 'Distribution', {
  // ...
  domainNames: [domainName],
  certificate: acm.Certificate.fromCertificateArn(this, 'Certificate', certificateArn),
  // ...
});

// Route 53レコードの作成
new route53.ARecord(this, 'AliasRecord', {
  zone: route53.HostedZone.fromHostedZoneAttributes(this, 'HostedZone', {
    hostedZoneId: 'ZXXXXXXXXXX',
    zoneName: 'example.com'
  }),
  target: route53.RecordTarget.fromAlias(new targets.CloudFrontTarget(distribution)),
  recordName: 'api'
});
```

4. **デプロイの実行**

```bash
cdk deploy
```

## ローカル環境でのデプロイ

ローカル環境でBacklogMCPを実行するには、以下の手順を実行します：

### 前提条件

- Python 3.10以上がインストールされていること
- Poetryがインストールされていること

### デプロイ手順

1. **リポジトリのクローン**

```bash
git clone https://github.com/yourusername/BacklogMCP.git
cd BacklogMCP
```

2. **環境変数の設定**

```bash
cp .env.example .env
# .envファイルを編集して必要な情報を入力
```

3. **依存関係のインストール**

```bash
poetry install
```

4. **仮想環境の有効化**

```bash
poetry shell
```

5. **アプリケーションの起動**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

6. **アプリケーションの確認**

ブラウザで以下のURLにアクセスして、アプリケーションが正常に動作していることを確認します：

```
http://localhost:8000/docs
```

## Docker Composeによるデプロイ

Docker Composeを使用してBacklogMCPをデプロイするには、以下の手順を実行します：

### 前提条件

- Dockerがインストールされていること
- Docker Composeがインストールされていること

### デプロイ手順

1. **リポジトリのクローン**

```bash
git clone https://github.com/yourusername/BacklogMCP.git
cd BacklogMCP
```

2. **環境変数の設定**

```bash
cp .env.example .env
# .envファイルを編集して必要な情報を入力
```

3. **Docker Composeでサービスを起動**

```bash
docker-compose -f docker/docker-compose.yml up -d
```

4. **アプリケーションの確認**

ブラウザで以下のURLにアクセスして、アプリケーションが正常に動作していることを確認します：

```
http://localhost:8000/docs
```

## 環境変数の設定

BacklogMCPを実行するには、以下の環境変数を設定する必要があります：

```
BACKLOG_API_KEY=your_backlog_api_key
BACKLOG_SPACE=your_backlog_space_name
BACKLOG_PROJECT=your_backlog_project_key
BACKLOG_DISABLE_SSL_VERIFY=false  # オプション：SSL検証を無効にする場合はtrue
```

### 環境変数の説明

- **BACKLOG_API_KEY**: Backlog APIキー。Backlogの「個人設定」→「API」から取得できます。
- **BACKLOG_SPACE**: Backlogのスペース名。URLの `https://{space}.backlog.jp` の `{space}` 部分です。
- **BACKLOG_PROJECT**: Backlogのプロジェクトキー。プロジェクト設定から確認できます。
- **BACKLOG_DISABLE_SSL_VERIFY**: SSL検証を無効にする場合は `true` に設定します。デフォルトは `false` です。

### 環境変数の設定方法

#### ローカル環境

`.env` ファイルに環境変数を設定します：

```
BACKLOG_API_KEY=your_backlog_api_key
BACKLOG_SPACE=your_backlog_space_name
BACKLOG_PROJECT=your_backlog_project_key
```

#### AWS Lambda

AWS Lambdaの環境変数設定で、以下の環境変数を設定します：

```
BACKLOG_API_KEY=your_backlog_api_key
BACKLOG_SPACE=your_backlog_space_name
BACKLOG_PROJECT=your_backlog_project_key
```

AWS CDKを使用してデプロイする場合は、以下のようにLambda関数に環境変数を設定します：

```typescript
// cdk/lib/backlog-mcp-stack.ts
const lambdaFunction = new lambda.Function(this, 'BacklogMCPFunction', {
  // ...
  environment: {
    BACKLOG_API_KEY: process.env.BACKLOG_API_KEY || '',
    BACKLOG_SPACE: process.env.BACKLOG_SPACE || '',
    BACKLOG_PROJECT: process.env.BACKLOG_PROJECT || '',
  },
  // ...
});
```

## デプロイ後の確認

デプロイが完了したら、以下の手順でアプリケーションが正常に動作していることを確認します：

### APIドキュメントの確認

ブラウザで以下のURLにアクセスして、APIドキュメントが表示されることを確認します：

```
http://localhost:8000/docs  # ローカル環境の場合
https://xxxxxxxxxx.cloudfront.net/docs  # AWS環境の場合
```

### APIエンドポイントの動作確認

curlコマンドを使用して、APIエンドポイントが正常に動作していることを確認します：

```bash
# プロジェクト一覧の取得
curl http://localhost:8000/api/projects  # ローカル環境の場合
curl https://xxxxxxxxxx.cloudfront.net/api/projects  # AWS環境の場合
```

### MCPエンドポイントの動作確認

MCPクライアント（例：Claude Desktop）を使用して、MCPエンドポイントが正常に動作していることを確認します：

1. MCPサーバーの追加
   - サーバー名: BacklogMCP
   - URL: http://localhost:8000/mcp  # ローカル環境の場合
   - URL: https://xxxxxxxxxx.cloudfront.net/mcp  # AWS環境の場合

2. プロンプトの実行
   ```
   プロジェクト一覧を取得して
   ```

## トラブルシューティング

### よくある問題と解決策

1. **AWS CDKデプロイエラー**

```
Error: This stack uses assets, so the toolkit stack must be deployed to the environment
```

解決策：CDKブートストラップを実行します。

```bash
cdk bootstrap
```

2. **Lambda関数のタイムアウト**

```
Task timed out after 30.00 seconds
```

解決策：Lambda関数のタイムアウト設定を増やします。

```typescript
// cdk/lib/backlog-mcp-stack.ts
const lambdaFunction = new lambda.Function(this, 'BacklogMCPFunction', {
  // ...
  timeout: cdk.Duration.seconds(60),  // タイムアウトを60秒に設定
  // ...
});
```

3. **APIキーの認証エラー**

```
{"detail":"Invalid API key"}
```

解決策：環境変数 `BACKLOG_API_KEY` が正しく設定されているか確認します。

4. **Docker Composeの起動エラー**

```
Error response from daemon: driver failed programming external connectivity on endpoint backlog-mcp
```

解決策：ポート8000が他のアプリケーションで使用されていないか確認します。

```bash
# ポート8000を使用しているプロセスを確認
lsof -i :8000
# または
netstat -tuln | grep 8000
```

5. **依存関係のインストールエラー**

```
Could not find a version that satisfies the requirement fastapi-mcp==0.3.3
```

解決策：Poetryのキャッシュをクリアして再試行します。

```bash
poetry cache clear pypi --all
poetry install
```

### ログの確認

#### ローカル環境

ローカル環境でのログは、コンソールに出力されます。

#### AWS Lambda

AWS Lambdaのログは、CloudWatch Logsで確認できます。

1. AWSマネジメントコンソールにログイン
2. CloudWatch Logsに移動
3. ロググループ `/aws/lambda/BacklogMCPStack-BacklogMCPFunction-XXXXXXXXXXXX` を選択
4. 最新のログストリームを選択

### サポート

問題が解決しない場合は、以下の方法でサポートを受けることができます：

1. GitHubのIssueを作成する
2. プロジェクトのメンテナーに連絡する
