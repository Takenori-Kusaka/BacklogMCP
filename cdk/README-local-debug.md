# CDKローカルデバッグガイド

このドキュメントでは、CDKのローカルデバッグ方法について説明します。

## 前提条件

- AWS CLI がインストールされていること
- Node.js と npm がインストールされていること
- AWS アカウントへのアクセス権があること

## 環境設定

CDKをローカルで実行するには、AWS認証情報を設定する必要があります。以下の方法で設定できます。

### 1. 環境変数を使用する方法

以下の環境変数を設定します：

```bash
export AWS_ACCESS_KEY_ID="あなたのアクセスキーID"
export AWS_SECRET_ACCESS_KEY="あなたのシークレットアクセスキー"
export AWS_SESSION_TOKEN="あなたのセッショントークン（必要な場合）"
export AWS_DEFAULT_REGION="us-east-1"
```

### 2. AWS CLIの設定を使用する方法

```bash
aws configure
```

### 3. 提供されているスクリプトを使用する方法

プロジェクトのルートディレクトリに以下のスクリプトが用意されています：

- `deploy-cdk.sh` - CDKをデプロイするためのスクリプト
- `dry-run-cdk.sh` - CDKのドライランを実行するためのスクリプト

これらのスクリプトを実行すると、AWS認証情報の入力を求められます。

## CDKコマンド

### CDKのビルド

```bash
cd cdk
npm run build
```

### CDKのシンセサイズ

```bash
cd cdk
npx cdk synth --context environment=dev
```

### CDKのドライラン

```bash
cd cdk
npx cdk deploy --all --dry-run --no-validate --context environment=dev
```

### CDKのデプロイ

```bash
cd cdk
npx cdk deploy --all --require-approval never --context environment=dev
```

## トラブルシューティング

### 1. Dockerイメージのビルドエラー

Dockerイメージのビルド時に以下のようなエラーが発生する場合：

```
ERROR: resolve : lstat ../docker: no such file or directory
```

これは、Dockerfileのパスが正しく設定されていないか、ビルドコンテキストが正しく設定されていないことが原因です。以下の点を確認してください：

- `cdk/lib/backlog-mcp-stack.ts`と`cdk/src/lib/backlog-mcp-stack.ts`ファイルのDockerイメージアセットのパスが正しく設定されているか
- `.dockerignore`ファイルが存在し、`cdk/cdk.out/`ディレクトリが無視されるように設定されているか

### 2. パスが長すぎるエラー

CDKがアセットをコピーする際に以下のようなエラーが発生する場合：

```
Error: ENAMETOOLONG: name too long, mkdir '...'
```

これは、CDKがDockerイメージをビルドする際に、ビルドコンテキストとして指定したディレクトリに`cdk/cdk.out`ディレクトリが含まれているため、再帰的にコピーしようとして無限ループに陥っていることが原因です。以下の点を確認してください：

- `.dockerignore`ファイルが存在し、`cdk/cdk.out/`ディレクトリが無視されるように設定されているか
- `cdk/lib/backlog-mcp-stack.ts`と`cdk/src/lib/backlog-mcp-stack.ts`ファイルの`ignoreMode: cdk.IgnoreMode.DOCKER`が設定されているか

### 3. AWS認証情報のエラー

AWS認証情報が正しく設定されていない場合、以下のようなエラーが発生する可能性があります：

```
Unable to locate credentials
```

この場合、AWS認証情報が正しく設定されているか確認してください。以下のコマンドを実行して、AWS認証情報が正しく設定されているか確認できます：

```bash
aws sts get-caller-identity
```

## 参考リンク

- [AWS CDK ドキュメント](https://docs.aws.amazon.com/cdk/latest/guide/home.html)
- [AWS CLI ドキュメント](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html)
