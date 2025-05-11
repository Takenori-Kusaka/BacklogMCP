# APIキーを使用したE2Eテスト

このガイドでは、デプロイされたAPI Gateway（認証にAPIキーが必要）に対してエンドツーエンド（E2E）テストを実行する方法について説明します。

## 前提条件

テストを実行する前に、以下が準備されていることを確認してください。

1.  **AWS CLIの設定**: AWS CLIが、対象のAWSアカウントおよびリージョンでAPI GatewayおよびCloudFormationにアクセスする権限を持つ認証情報で設定されていること。
2.  **Poetryのインストール**: このプロジェクトでは、依存関係の管理にPoetryを使用しています。Poetryがインストールされ、プロジェクトの依存関係がインストールされていること (`poetry install`)。
3.  **CDKデプロイの完了**: AWS CDKスタック（`backlog-mcp-stack`）が正常にデプロイされていること。

## E2Eテストの実行手順

### 1. 必要な情報を収集する

CDKスタックのデプロイから以下の情報が必要になります。

*   **APIキーID**:
    *   AWS CloudFormationコンソールのスタック（例: `backlog-mcp-dev-stack`）の「出力」タブで、`ApiKeyId` キーを探します。
    *   または、AWS CLIを使用します:
        ```bash
        aws cloudformation describe-stacks --stack-name <YOUR_CDK_STACK_NAME> --query "Stacks[0].Outputs[?OutputKey=='ApiKeyId'].OutputValue" --output text
        ```
        （`<YOUR_CDK_STACK_NAME>` を実際のスタック名に置き換えてください。例: `backlog-mcp-dev-stack`）

*   **デプロイされたAPIエンドポイントURL**:
    *   これは通常、CloudFrontディストリビューションのドメイン名になります。CloudFormationコンソールの出力で `CloudFrontDomain` として見つけます。
    *   または、AWS CLIを使用します:
        ```bash
        aws cloudformation describe-stacks --stack-name <YOUR_CDK_STACK_NAME> --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDomain'].OutputValue" --output text
        ```
    *   完全なエンドポイントURLは `https://<CloudFrontDomain>` となります。CloudFrontを使用していない場合や、API Gatewayを直接テストしたい場合は、`ApiGatewayUrl` の出力を使用してください。

*   **AWSリージョン**: CDKスタックがデプロイされているAWSリージョン（例: `ap-northeast-1`）。

*   **Backlogプロジェクトキー（任意）**: 特定のBacklogプロジェクトと連携するテスト（`test_get_project_by_key_direct` など）を実行する場合は、Backlogインスタンスの有効なプロジェクトキーが必要になります。

### 2. APIキーの値を取得する

前の手順で取得したAPIキーIDは、認証に必要な実際のキーの値ではありません。提供されているスクリプトを使用してキーの値を取得します。

```bash
poetry run python scripts/get_api_key_value.py --api-key-id <YOUR_API_KEY_ID> --region <YOUR_AWS_REGION>
```

*   `<YOUR_API_KEY_ID>` を収集したIDに置き換えます。
*   `<YOUR_AWS_REGION>` をデプロイリージョンに置き換えます。

このコマンドは、APIキーの値をコンソールに出力します。**この値を安全にコピーしてください。**

### 3. 環境変数を設定する

テストを実行する前に、ターミナルセッションで以下の環境変数を設定します。

```bash
export DEPLOYED_API_ENDPOINT="https://<YOUR_CLOUDFRONT_DOMAIN_OR_API_GATEWAY_URL>"
export DEPLOYED_API_KEY="<YOUR_COPIED_API_KEY_VALUE>"
export AWS_REGION="<YOUR_AWS_REGION>"

# 任意: 特定のBacklogプロジェクトを必要とするテストの場合
# export BACKLOG_PROJECT="<YOUR_BACKLOG_PROJECT_KEY>"
```

*   プレースホルダーを実際の値に置き換えてください。

### 4. Pytest E2Eテストを実行する

Poetryを使用してE2Eテストを実行します。

```bash
poetry run pytest tests/e2e/test_project_api_direct.py
```

これで、デプロイされたAPI Gatewayに対して、提供されたAPIキーを使用してテストが実行されます。テスト結果の出力を確認してください。

## トラブルシューティング

*   **認証エラー（401/403）**:
    *   `DEPLOYED_API_KEY` が `get_api_key_value.py` から取得した値で正しく設定されていることを再確認してください。
    *   使用したAPIキーIDが正しく、API Gatewayでキーが有効になっていることを確認してください。
    *   API Gatewayステージが使用量プランとAPIキーに正しく関連付けられていることを確認してください。
*   **接続エラー**:
    *   `DEPLOYED_API_ENDPOINT` が正しく、アクセス可能であることを確認してください。
    *   リクエストをブロックしている可能性のあるWAFルールやネットワーク設定を確認してください。
*   **`get_api_key_value.py` スクリプトエラー**:
    *   AWS CLIが必要な権限（`apigateway:GET`）で正しく設定されていることを確認してください。
    *   `api-key-id` および `region` 引数が正しいことを確認してください。