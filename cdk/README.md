# CloudFront + API Gateway + Lambda（Web Adapter）によるFastAPIホスティングアーキテクチャ設計書

## 開発環境要件

本プロジェクトの開発・テスト・デプロイには以下の環境が必要です：

| ツール/ライブラリ | 必須バージョン | 備考 |
|-----------------|--------------|------|
| Node.js | 14.15.0以上 | 16.x以上推奨 |
| npm | 6.14.0以上 | Node.jsに付属 |
| AWS CDK | 2.x | `npm install -g aws-cdk` でインストール |
| TypeScript | 4.9.x以上 | `npm install -g typescript` でインストール |
| Python | 3.10以上 | FastAPI実装用 |
| Docker | 最新版 | Lambdaコンテナイメージビルド用 |

**注意**: Node.js 12.x以下では、AWS CDKライブラリの一部機能（オプショナルチェイニングなど）が正常に動作しません。必ず14.15.0以上のバージョンを使用してください。

## 開発手順

### 環境セットアップ

1. 必要なツールのインストール
   ```bash
   # Node.jsのインストール（14.x以上）
   curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash - && sudo apt-get install -y nodejs

   # 依存パッケージのインストール
   cd cdk
   npm install
   ```

2. ビルド
   ```bash
   npm run build
   ```

### テスト実行

テストを実行する前に、Node.jsのバージョンが14.15.0以上であることを確認してください。

```bash
# 通常のテスト実行
npm test

# Node.jsバージョンチェック付きテスト実行（推奨）
npm run test:safe
```

#### テスト結果の確認

テストが失敗した場合や詳細な結果を確認したい場合は、`cdk`ディレクトリ直下に生成される `test-results.log` を確認してください。
このファイルには、テスト実行時の標準出力と標準エラー出力が記録されています。

```bash
# test-results.log を確認する例
cat test-results.log
```

**注意:** `test-results.log` は `.gitignore` に登録されており、Gitの追跡対象外です。

### ローカルでのCDKコード検証

デプロイ前にローカル環境でCDKコードの妥当性を確認することで、エラーを早期に発見できます。

1.  **前提条件の確認**:
    *   **AWS認証情報**: ローカル環境でAWS CLIが設定され、CDKがデプロイ対象のAWSアカウント・リージョンにアクセスできる認証情報（アクセスキー、シークレットキー、セッショントークン、または名前付きプロファイル）が正しく設定されていることを確認してください。
        ```bash
        aws sts get-caller-identity
        ```
    *   **Node.jsとnpm**: 本ドキュメントの「開発環境要件」セクション記載のバージョン要件を満たしていることを確認してください。
    *   **AWS CDK CLI**: グローバルにインストールされていることを確認してください。
        ```bash
        npm install -g aws-cdk
        cdk --version
        ```
    *   **プロジェクト依存関係**: `cdk` ディレクトリで必要なNode.jsモジュールがインストールされていることを確認してください。
        ```bash
        cd cdk
        npm install # または npm ci
        cd ..
        ```

2.  **`cdk synth` (スタックの合成)**:
    CloudFormationテンプレートを生成し、構文エラーなどがないか確認します。
    ターミナルで `cdk` ディレクトリに移動し、以下のコマンドを実行します。
    ```bash
    cd cdk
    # 例: dev環境の場合
    cdk synth --context environment=dev
    
    # 例: prod環境で、アラートメールも指定する場合 (alertEmailはスタックのPropsで定義されていれば)
    # cdk synth --context environment=prod --context alertEmail=your-alert-email@example.com
    cd ..
    ```
    エラーメッセージが表示されず、CloudFormationテンプレートが標準出力に表示されれば、基本的な合成は成功です。

3.  **`cdk diff` (差分確認 - オプション)**:
    もし既に対象環境にデプロイ済みのスタックがある場合、現在のコードとの差分を確認できます。
    ```bash
    cd cdk
    # 例: dev環境の場合
    cdk diff --context environment=dev
    cd ..
    ```

4.  **`cdk deploy --dry-run` (デプロイのドライラン - オプション)**:
    実際にAWSリソースに変更を加えることなく、デプロイプロセスをシミュレートします。必要なIAM権限のチェックなども行われます。
    ```bash
    cd cdk
    # 例: dev環境で、AWSプロファイル 'your-profile' を使用する場合
    # aws-vault exec your-profile -- cdk deploy --dry-run --context environment=dev
    # または、プロファイルがデフォルト設定されていれば
    # cdk deploy --dry-run --context environment=dev
    cd ..
    ```
    `aws-vault exec your-profile --` の部分は、ご自身のAWS認証情報の管理方法に合わせて調整してください。
    エラーが発生しなければ、デプロイに必要な準備（権限など）が整っている可能性が高いです。

これらのコマンドをローカルで実行し、問題がないことを確認した上でコミット・プッシュすることを推奨します。

### デプロイ

環境ごとにデプロイコマンドが用意されています：

```bash
# 開発環境へのデプロイ
npm run deploy:dev

# ステージング環境へのデプロイ
npm run deploy:stg

# 本番環境へのデプロイ
npm run deploy:prod
```

AWS環境におけるFastAPIアプリケーションのサーバーレスホスティングアーキテクチャを設計するにあたり、主要コンポーネントの連携とCDK実装戦略を詳細に検討します。本設計ではパフォーマンス最適化、セキュリティ強化、運用効率化の観点から技術選定を行いました[1][2][9][12]。

## アーキテクチャ全体像
### 論理構成図
```
┌──────────────────────────┐       ┌───────────────────┐
│ クライアント             │       │ Amazon CloudFront  │
│ (HTTPSリクエスト + APIキー) ├───────► セキュリティレイヤー   │
└──────────────────────────┘       └─────────┬─────────┘
                                             │
                                  ┌──────────▼──────────┐
                                  │ API Gateway HTTP    │
                                  │ (FastAPIホスティング)  │
                                  └──────────┬──────────┘
                                             │
                                  ┌──────────▼──────────┐
                                  │ AWS Lambda          │
                                  │ (FastAPI + Web Adapter) │
                                  └──────────────────────┘
```

### コンポーネント特性比較
| 要素               | 技術選定理由                                                                 | 代替案リスク分析                     |
|--------------------|----------------------------------------------------------------------------|-----------------------------------|
| Lambda Web Adapter | 既存FastAPIコードの変更不要、ASGI互換性[2][11][20]                          | Mangum利用時はハンドラ修正必要[1][16]    |
| CloudFront         | セキュリティヘッダー管理、WAF連携、カスタムドメイン管理[9][12][17]           | 直接API Gateway公開時のレイテンシ増加    |
| API Gateway HTTP   | FastAPIのHTTPホスティング、APIキー認証、低コスト[4][6]                      | REST APIと比較して一部機能制限あり     |
| CDK構成            | インフラのコード化、マルチリージョン展開可能性[5][7][9]                      | Terraform等他ツールとの統合難易度      |

## Lambda関数設計詳細
### Dockerfile最適化戦略
```dockerfile
FROM public.ecr.aws/lambda/python:3.10
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.9.1 /lambda-adapter /opt/extensions/lambda-adapter

WORKDIR /var/task
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

ENV TZ=Asia/Tokyo
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```
・ベースイメージ：AWS公式Pythonイメージ（サイズ最適化）[1][5]  
・Web Adapter導入：Lambdaランタイムとの互換性確保[2][11]  
・タイムゾーン設定：日本時間準拠のログ管理[2]  
・マルチステージビルド：本番用イメージサイズ最小化[5][7]  

### パフォーマンスチューニング
```python
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI(root_path="/prod/")

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

handler = Mangum(app, lifespan="off")
```
・Cold Start対策：Lambdaプロビジョン済みコンカレンシー設定[5][18]  
・メモリ最適化：256MB～3008MB間でベンチマーク実施[5][18]  
・X-Rayトレース：リクエストフロー可視化[9][17]  

## API Gateway構成設計
### セキュリティ設計マトリックス
| 脅威シナリオ         | 対策手法                          | CDK実装方法                          |
|----------------------|-----------------------------------|-------------------------------------|
| APIキー漏洩          | 使用量プランによる回数制限[4][6]   | UsagePlan.addApiKey()               |
| DDoS攻撃             | レート制限＋WAF連携[4][6]         | ThrottleSettings                    |
| 不正パラメータ       | リクエストバリデーション           | Modelの追加とメソッド統合            |
| 中間者攻撃           | CloudFront HTTPS強制[9][12]       | ViewerProtocolPolicy: HTTPS_ONLY   |

### 使用量プラン設計例
```typescript
const usagePlan = new UsagePlan(this, 'ApiUsagePlan', {
  throttle: {
    rateLimit: 100,
    burstLimit: 50
  },
  quota: {
    limit: 10000,
    period: Period.MONTH
  }
});

const apiKey = new ApiKey(this, 'ApiKey', {
  description: 'Customer API Key'
});

usagePlan.addApiKey(apiKey);
```
・階層型プラン設計：基本/プレミアムプランの併用[4][6]  
・アラート設定：CloudWatch連携による閾値通知[4][6]  
・キーローテーション：CDKデプロイ時の自動更新機能[6]  

## CloudFront統合設計
### 環境ごとのCloudFront統合設計（Agent対応）
#### セキュリティ・WAF・ログ・出力例

| 環境 | キャッシュTTL | WAF | CloudWatchアラーム | ログ保持 | プロビジョンド同時実行数 |
|------|--------------|-----|-------------------|----------|-------------------------|
| dev  | 0秒 (無効)   | 無  | 無                | 14日     | なし                    |
| stg  | 0秒 (無効)   | オプション | 無         | 14日     | なし                    |
| prod | 0秒 (無効)   | オプション | 有         | 30日     | なし                    |

**注意**: 
- CloudFrontのキャッシュは、Backlogのチケット更新をリアルタイムに反映するため、基本的に無効化しています
- WAFはコスト対効果を考慮し、オプション機能として実装しています（必要に応じて有効化）
- Lambdaのプロビジョンド同時実行数は、コスト最適化のため無効としています

```typescript
new cloudfront.Distribution(this, 'ApiDistribution', {
  defaultBehavior: {
    origin: new origins.RestApiOrigin(api),
    cachePolicy: new cloudfront.CachePolicy(this, 'ApiCachePolicy', {
      defaultTtl: Duration.seconds(env === 'prod' ? 30 : env === 'stg' ? 10 : 5),
      maxTtl: Duration.seconds(env === 'prod' ? 30 : env === 'stg' ? 10 : 5),
      enableAcceptEncodingBrotli: true,
      enableAcceptEncodingGzip: true
    }),
    viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
    responseHeadersPolicy: new cloudfront.ResponseHeadersPolicy(this, 'SecurityHeaders', {
      securityHeadersBehavior: {
        contentTypeOptions: { override: true },
        frameOptions: { frameOption: cloudfront.HeadersFrameOption.DENY, override: true },
        referrerPolicy: { referrerPolicy: cloudfront.HeadersReferrerPolicy.SAME_ORIGIN, override: true },
        strictTransportSecurity: { accessControlMaxAge: Duration.seconds(31536000), includeSubdomains: true, override: true, preload: true },
        xssProtection: { protection: true, modeBlock: true, override: true }
      }
    })
  },
  ...(env !== 'dev' && { webAclId: wafAcl.attrArn }),
  // ログ設定・Geo制限・他
});
```
・キャッシュTTL: dev=5秒, stg=10秒, prod=30秒  
・セキュリティヘッダー: Content-Type-Options, Frame-Options, Referrer-Policy, Strict-Transport-Security, XSS-Protection  
・HTTPS強制  
・WAF（stg/prodのみ）: SQLインジェクション/レート制限  
・CloudWatchアラーム（prodのみ）: Lambda/API Gateway 5xx/SNS通知  
・ログ保持: dev/stg=14日, prod=30日  
・Stack Outputs: 環境名/API Gateway URL/CloudFrontドメイン名/APIキーID  
・Lambda: dev=512MB, stg=1024MB, prod=2048MB, タイムアウト30秒, prodのみプロビジョンド同時実行数10, 環境変数（TZ/NODE_ENV/LOG_LEVEL）

### セキュリティ強化設計
```typescript
const responseHeadersPolicy = new cloudfront.ResponseHeadersPolicy(this, 'SecurityHeaders', {
  securityHeadersBehavior: {
    contentTypeOptions: { override: true },
    frameOptions: { frameOption: HeadersFrameOption.DENY, override: true },
    referrerPolicy: { referrerPolicy: HeadersReferrerPolicy.SAME_ORIGIN, override: true },
    strictTransportSecurity: { 
      accessControlMaxAge: Duration.seconds(63072000),
      includeSubdomains: true,
      override: true,
      preload: true
    },
    xssProtection: { protection: true, modeBlock: true, override: true }
  }
});
```
・HSTS強化：1年間のキャッシュ有効化[9][17]  
・XSS保護：モダンブラウザ対応ポリシー[9][17]  
・CORS制御：オリジン限定アクセス許可[12]  

## CDKスタック設計
### 主要コンストラクト依存関係
```
ApiStack
├── FastAPILambda
├── HttpApiGateway
└── ApiKey (オプション)

CloudFrontStack
└── Distribution
    └── HttpApiOrigin (ApiGateway)
```

### マルチ環境展開戦略
```typescript
interface ApiStackProps extends cdk.StackProps {
  stageName: string;
  rateLimit: number;
  burstLimit: number;
}

const devProps: ApiStackProps = {
  stageName: 'dev',
  rateLimit: 100,
  burstLimit: 50
};

const prodProps: ApiStackProps = {
  stageName: 'prod',
  rateLimit: 1000,
  burstLimit: 500
};
```
・環境変数分離：dev/stg/prodごとのパラメータ管理[5][7]  
・Pipeline連携：CDK Pipelineによる自動デプロイ[5][7]  
・Rollback戦略：Canaryデプロイメント[5][7]  

## 認証フロー詳細
### APIキー検証シーケンス
```
1. クライアント → CloudFront : HTTPSリクエスト（x-api-keyヘッダ）
2. CloudFront → API Gateway : リクエスト転送
3. API Gateway → 使用量プラン : キー有効性確認
4. 使用量プラン → カウンタ : 呼び出し回数チェック
5. API Gateway → Lambda : リクエスト転送
6. Lambda → FastAPI : リクエスト処理
```
・二段階検証：APIキー有効性＋使用量制限[4][6]  
・監査ログ：CloudTrail連携によるAPI操作記録[4][6]  
・緊急遮断：APIキーの無効化機能[4][6]  

## 障害対策設計
### フェイルセーフメカニズム
| 障害シナリオ         | 影響範囲       | 復旧戦略                          |
|----------------------|----------------|-----------------------------------|
| Lambdaタイムアウト   | 部分障害       | プロビジョン済みコンカレンシー増加  |
| API Gateway制限超過  | サービス停止   | オートスケーリング連携[4][6]       |
| CloudFrontキャッシュ不整合 | データ不整合 | キャッシュ無効化API連動[9][17]     |
| 使用量プランカウンタ不具合 | 課金誤差      | マネージドサービス連携再同期[4][6] |

## コスト最適化戦略
### 主要サービスコスト内訳
| サービス         | コスト要因                  | 最適化手法                          |
|------------------|-----------------------------|-------------------------------------|
| Lambda          | 実行時間×メモリサイズ       | プロビジョン済みコンカレンシー活用[5] |
| API Gateway     | リクエスト数＋データ転送量   | キャッシュ効率化[9][17]              |
| CloudFront       | リクエスト数＋データ転送量   | 圧縮設定最適化[9][17]                |
| CloudWatch      | ログ保存量＋メトリクス数     | ログ保持期間設定（14日）[5]           |

### コスト見積もり例（月間100万リクエスト）
```
・Lambda: 1Mリクエスト × 平均実行時間1秒 × 512MB = $X.XX
・API Gateway: 1M REST API呼び出し = $Y.YY
・CloudFront: 1Mリクエスト + 100GB転送 = $Z.ZZ
・合計見積もり: $X+Y+Z ≈ $AAA
```

## デプロイパイプライン
### CI/CDフロー設計
```
1. コードコミット → GitHub Actions起動
2. ユニットテスト実行（pytest）
3. Dockerイメージビルド＆ECRプッシュ
4. CDK Synthesize
5. ステージング環境デプロイ
6. 結合テスト実行（Postman）
7. 本番環境Blue-Greenデプロイ
```
・ロールバック戦略：以前のイメージタグ保持[5][7]  
・Canary分析：CloudWatchメトリクス監視[5][7]  
・シークレット管理：AWS Secrets Manager連携[5][7]  

## 監視・運用設計
### CloudWatchダッシュボード例
```
・Lambdaメトリクス：実行時間、エラー率、スロットル
・API Gateway：4XX/5XXエラー、キャッシュヒット率
・CloudFront：リクエスト分布、転送量
・使用量プラン：APIキー別使用状況
```
・アラート閾値：エラー率5%超過時に通知[4][5]  
・自動修復：Lambda関数の自動再デプロイ[5][7]  
・ログ分析：CloudWatch Logs Insights連携[5][7]  

## セキュリティ監査項目
### 必須対応項目一覧
```
□ APIキーの暗号化保存（AWS KMS連携）
□ WAFによるSQLインジェクション対策
□ IAMロールの最小権限原則適用
□ 脆弱性スキャン（ECR連携）
□ セキュリティグループの不必要なポート開放排除
```
・定期的ペネトレーションテスト[4][12]  
・SOC2/ISO27001準拠監査[4][12]  
・サードパーティライブラリ監視（Dependabot）[5][7]  

本設計書で提案したアーキテクチャは、FastAPIアプリケーションのサーバーレスホスティングにおいて、パフォーマンスとセキュリティの最適なバランスを実現します。CDKによるインフラのコード化により、環境間の整合性保持と変更管理の効率化が可能となります[5][7][9]。実際の実装時には、各組織のセキュリティポリシーやコンプライアンス要件に合わせた微調整が必要となりますが、本設計をベースに拡張可能な構造を採用しています。

Citations:
[1] https://zenn.dev/alleeks/articles/a286144465cb6b
[2] https://note.com/minato_kame/n/nff628b4c2f91
[3] https://qiita.com/hibohiboo/items/0026418971669aa1cf77
[4] https://dev.classmethod.jp/articles/try-api-gateway-usage-plan/
[5] https://www.ranthebuilder.cloud/post/build-aws-lambda-container-image-with-aws-cdk
[6] https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_apigateway.UsagePlan.html
[7] https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda.DockerImageFunction.html
[8] https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_cloudfront_origins.RestApiOrigin.html
[9] https://docs.aws.amazon.com/solutions/latest/constructs/aws-cloudfront-apigateway.html
[10] https://aws.amazon.com/jp/builders-flash/202304/api-development-sam-fastapi-mangum/
[11] https://github.com/awslabs/aws-lambda-web-adapter/blob/main/examples/fastapi/README.md
[12] https://qiita.com/zhang_hang/items/b24a4a75579ca65e0193
[13] https://dev.classmethod.jp/articles/change-default-dateway-response-configuration-for-api-gateway-reat-api/
[14] https://github.com/patheard/aws-fastapi-lambda
[15] https://dev.classmethod.jp/articles/build-private-cloudfront-and-authentication-api-with-aws-cdk/
[16] https://zenn.dev/hayata_yamamoto/articles/781efca1687272
[17] https://docs.aws.amazon.com/solutions/latest/constructs/aws-cloudfront-apigateway.html
[18] https://www.deadbear.io/simple-serverless-fastapi-with-aws-lambda/
[19] https://github.com/aws/aws-cdk/issues/32332
[20] https://github.com/Kludex/mangum
[21] https://serverlessland.com/patterns/cloudfront-s3-lambda-cdk
[22] https://qiita.com/Shinkijigyo_no_Hitsuji/items/cedd1825e5437663d3ce
[23] https://dev.classmethod.jp/articles/aws-lambda-web-adapter-fastapi-bedrock-chatdemo/
[24] https://stackoverflow.com/questions/78094087/how-do-i-correctly-route-fastapi-on-aws-lambda-using-mangum-to-avoid-a-not-foun
[25] https://github.com/awslabs/aws-lambda-web-adapter/blob/main/examples/fastapi-response-streaming/README.md
[26] https://zenn.dev/youyo/articles/lwa-fastapi-cdk
[27] https://qiita.com/moritalous/items/f828c5d7d2d116884f9a
[28] https://speakerdeck.com/tmokmss/aws-lambda-web-adapterwohuo-yong-suruxin-siisabaresunoshi-zhuang-patan
[29] https://aws.amazon.com/jp/builders-flash/202301/lambda-web-adapter/
[30] https://github.com/aws/aws-cdk/discussions/22944
[31] https://qiita.com/ou-mori/items/d2a2a12d3cc68201abbe
[32] https://dev.classmethod.jp/articles/aws-cdk-api-version-management-mastering-system-configuration-and-deployment-with-github-actions/
[33] https://docs.aws.amazon.com/ja_jp/apigateway/latest/developerguide/api-gateway-api-usage-plans.html
[34] https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda.DockerImageFunction.html
[35] https://zenn.dev/hikapoppin/articles/559cf40a50af7e
[36] https://qiita.com/syukan3/items/f8ed0226a7e7a7f6bc81
[37] https://aws.amazon.com/jp/blogs/news/developing-microservices-using-container-image-support-for-aws-lambda-and-aws-cdk/
[38] https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_cloudfront-readme.html
[39] https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_apigateway.UsagePlan.html
[40] https://qiita.com/coleyon/items/aecec1337786bced12c1
[41] https://www.ogis-ri.co.jp/otc/hiroba/technical/cdk-concepts/part4.html
[42] https://github.com/aws/aws-cdk/issues/8367
[43] https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_apigateway/UsagePlan.html
[44] https://stackoverflow.com/questions/77440359/how-do-i-configure-dockerized-lambda-image-configuration-with-cdk
[45] https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_cloudfront_origins/RestApiOrigin.html
[46] https://qiita.com/onose004/items/47613e48bb0a690470c0
[47] https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_lambda/DockerImageFunction.html
[48] https://github.com/aws/aws-cdk/issues/32332
[49] https://qiita.com/the_red/items/7ec40e078e042a3629ec
[50] https://github.com/aws/aws-cdk/issues/26987
[51] https://zenn.dev/watany/scraps/efe9e946680bbf
[52] https://weirdsheeplabs.com/blog/database-migrations-fastapi-alembic-aws-lambda
[53] https://zenn.dev/monjara/articles/38443c05723f1b
[54] https://zenn.dev/big_tanukiudon/articles/e1d05230f1c5ab
[55] https://qiita.com/liveinvalley/items/897ce282a113a93bb7ff
[56] https://zenn.dev/youyo/articles/huma-lambda-cdk
[57] https://qiita.com/ren8k/items/8525fb170c13ec861857
[58] https://www.docswell.com/s/_n13u_/ZEX99Q-2025-01-18-135732
[59] https://zenn.dev/ncdc/articles/f959131cf5f4b5
[60] https://qiita.com/taka---tech/items/b9ce6a9eb7b7e9dfc0f6
[61] https://fastapi.tiangolo.com/ja/external-links/
[62] https://zenn.dev/bohebohe/scraps/bcf3bac0d2cc13
[63] https://docs.aws.amazon.com/cdk/api/v2/java/software/amazon/awscdk/services/apigateway/RestApi.html
[64] https://github.com/aws/aws-cdk/discussions/26991
[65] https://stackoverflow.com/questions/75844275/how-can-i-configure-an-api-gateway-endpoint-to-require-an-api-key
[66] https://www.tate-blog.com/2024/02/26/express-on-lambda/
[67] https://github.com/aws-samples/lambda-web-adapter-benchmark-sample
[68] https://github.com/awslabs/aws-lambda-web-adapter
[69] https://inoccu.com/blog/2024/02/14/011624.html
[70] https://community.aws/content/2fJxs6oeXINRtG18bXmou7nea5i/adding-flexibility-to-your-deployments-with-lambda-web-adapter
[71] https://wptech.kiichiro.work/617bivwxur/

---
Perplexity の Eliot より: pplx.ai/share
