# FastAPIをLambda Web Adapterで実装するCDKソリューション

FastAPIをLambda Web Adapterと連携させ、ライブラリをレイヤーとして分離してデプロイするための最適なCDKソリューションについてまとめました。デバッグやビルド時間の短縮に役立つアプローチを解説します。

## 推奨されるCDKライブラリ

FastAPIをLambda Web Adapter経由でデプロイするなら、`@aws-cdk/aws-lambda-python-alpha`が最適なCDKライブラリです。Alpha版ではありますが、Python Lambda関数とレイヤーを効率的に管理できる機能を提供しています[8]。

## 実装例

以下に、FastAPIアプリケーションをLambda Web Adaptorと連携させるCDKの実装例を示します：

```typescript
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as python from '@aws-cdk/aws-lambda-python-alpha';
import * as apigw from 'aws-cdk-lib/aws-apigatewayv2';
import { HttpLambdaIntegration } from 'aws-cdk-lib/aws-apigatewayv2-integrations';
import { Construct } from 'constructs';

export class FastApiLambdaStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // FastAPIの依存ライブラリをレイヤーとして作成
    const layer = new python.PythonLayerVersion(this, "FastApiLayer", {
      entry: "src/layer",  // requirements.txtがあるディレクトリ
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_11],
      compatibleArchitectures: [lambda.Architecture.ARM_64],
    });

    // Lambda関数の作成
    const func = new lambda.Function(this, "FastApiFunction", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "run.sh",  // シェルスクリプトハンドラー
      code: lambda.Code.fromAsset("src/app"),  // FastAPIアプリケーションコード
      architecture: lambda.Architecture.ARM_64,
      timeout: cdk.Duration.seconds(30),
      layers: [
        layer,
        // Lambda Web Adapterをレイヤーとして追加
        lambda.LayerVersion.fromLayerVersionArn(
          this,
          "LambdaAdapterLayerArm64",
          "arn:aws:lambda:ap-northeast-1:753240598075:layer:LambdaAdapterLayerArm64:24"
        ),
      ],
      environment: {
        PYTHONPATH: "/opt/python",
        PORT: "8000",
        AWS_LAMBDA_EXEC_WRAPPER: "/opt/bootstrap",
      },
    });

    // HTTP API Gatewayの作成と関数の統合
    const api = new apigw.HttpApi(this, "FastApiHttpApi", {
      apiName: "fastapi-lambda-api",
      defaultIntegration: new HttpLambdaIntegration("FastApiIntegration", func),
    });

    // 出力としてAPIのURLを表示
    new cdk.CfnOutput(this, "ApiUrl", {
      value: api.apiEndpoint,
    });
  }
}
```

## ファイル構造

このソリューションを実装するためのディレクトリ構造は以下のようになります：

```
my-fastapi-lambda/
├── cdk.json
├── src/
│   ├── layer/
│   │   └── requirements.txt   # FastAPI、uvicornなどの依存関係
│   └── app/
│       ├── main.py            # FastAPIアプリケーションコード
│       └── run.sh             # 起動スクリプト
└── lib/
    └── fastapi-lambda-stack.ts  # CDKスタック定義
```

## 起動スクリプトの作成

`src/app/run.sh`には以下のような内容を記述します：

```bash
#!/bin/bash
python -m uvicorn main:app --proxy-headers --host 0.0.0.0 --port ${PORT}
```

このスクリプトに実行権限を付与することを忘れないでください：
```bash
chmod +x src/app/run.sh
```

## FastAPIアプリケーションの例

`src/app/main.py`には通常のFastAPIアプリケーションを記述します：

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI on Lambda!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

## 実装時の注意点

1. **PYTHONPATHの設定**: Lambda内でPythonがレイヤー内のライブラリを正しく認識するためには、環境変数`PYTHONPATH`の設定が重要です[8]。

2. **スクリプトハンドラー**: Lambda Web Adapterを使用する場合、`handler`パラメータには関数名ではなく起動スクリプトのパス(`run.sh`)を指定します[3][8]。

3. **レイヤーARN**: Lambda Web AdapterのレイヤーARNはリージョンに依存するため、デプロイ先のリージョンに合わせて調整が必要です[8]。

## 利点

このアプローチの主な利点は：

1. アプリケーションコードとライブラリを分離することで、コード変更時のデプロイ時間が短縮されます[8]。
2. Lambda Web Adapterを使用することで、FastAPIアプリケーションのコードを変更せずにそのままLambdaで実行できます[3]。
3. `@aws-cdk/aws-lambda-python-alpha`を使用することで、Pythonの依存関係管理が簡素化されます[8][2]。

このソリューションにより、Dockerコンテナ全体をビルドする必要がなく、デバッグやビルド時間の短縮が可能になります。

Citations:
[1] https://qiita.com/haruki-lo-shelon/items/2eb7c05f1dd3d4df2ca9
[2] https://qiita.com/takmot/items/8c6aa3961f93102e2316
[3] https://note.com/minato_kame/n/nff628b4c2f91
[4] https://www.ranthebuilder.cloud/post/build-aws-lambda-layers-with-aws-cdk
[5] https://www.tate-blog.com/2024/02/26/express-on-lambda/
[6] https://zenn.dev/youyo/articles/huma-lambda-cdk
[7] https://zenn.dev/tnakano/articles/036a1b87082296
[8] https://zenn.dev/youyo/articles/lwa-fastapi-cdk
[9] https://github.com/awslabs/aws-lambda-web-adapter
[10] https://github.com/mirumee/lynara
[11] https://pypi.org/project/asgi-aws/
[12] https://zenn.dev/takakura_tech/articles/aws-localstack-cdk-lambda-fastapi
[13] https://aws.amazon.com/jp/builders-flash/202301/lambda-web-adapter/
[14] https://community.aws/content/2fJxs6oeXINRtG18bXmou7nea5i/adding-flexibility-to-your-deployments-with-lambda-web-adapter
[15] https://github.com/aws-samples/lambda-web-adapter-benchmark-sample
[16] https://qiita.com/eno49conan/items/6d3e98df2ac82613c3b3
[17] https://zenn.dev/big_tanukiudon/articles/e1d05230f1c5ab
[18] https://github.com/youyo/lwa-fastapi
[19] https://wptech.kiichiro.work/617bivwxur/
[20] https://blog.morifuji-is.ninja/post/2023-11-04/
[21] https://docs.aws.amazon.com/cdk/api/v2/docs/aws-lambda-python-alpha-readme.html
[22] https://dev.classmethod.jp/articles/aws-lambda-web-adapter-fastapi-bedrock-chatdemo/
[23] https://zenn.dev/takoyaki3/articles/fe7d180c4bb71d
[24] https://how.wtf/serverless-fastapi-with-aws-lambda-api-gateway-and-aws-cdk.html
[25] https://dev.classmethod.jp/articles/aws-cdk-lambda-python-snapstart/
[26] https://qiita.com/moritalous/items/f828c5d7d2d116884f9a
[27] https://zenn.dev/collabostyle/articles/2596792d6075e7
[28] https://note.com/iwata9999/n/nf7da6fbd5c7b
[29] https://www.npmjs.com/package/@aws-cdk/aws-lambda-python-alpha
[30] https://github.com/awslabs/aws-lambda-web-adapter/blob/main/examples/fastapi/README.md
[31] https://blog.i-tale.jp/2020/11/d2/
[32] https://www.ajisaba.net/develop/aws/cdk/nextjs_cdk_project_lambda.html
[33] https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/lambda-cdk-tutorial.html
[34] https://weirdsheeplabs.com/blog/fastapi-deployments-with-aws-lambda-and-cdk
[35] https://zenn.dev/where/articles/f2fc3caf93ec6c
[36] https://qiita.com/liveinvalley/items/897ce282a113a93bb7ff
[37] https://qiita.com/haruki-lo-shelon/items/2eb7c05f1dd3d4df2ca9
[38] https://speakerdeck.com/tmokmss/aws-lambda-web-adapterwohuo-yong-suruxin-siisabaresunoshi-zhuang-patan
[39] https://github.com/awslabs/aws-lambda-web-adapter
[40] https://zenn.dev/monjara/articles/38443c05723f1b
[41] https://zenn.dev/takakura_tech/articles/aws-localstack-cdk-lambda-fastapi
[42] https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_autoscaling.AutoScalingGroup.html
[43] https://qiita.com/eno49conan/items/6d3e98df2ac82613c3b3
[44] https://aws.amazon.com/jp/blogs/news/leverage-l2-constructs-to-reduce-the-complexity-of-your-aws-cdk-application/
[45] https://zenn.dev/youyo/articles/huma-lambda-cdk
[46] https://blog.appsignal.com/2024/03/27/building-serverless-apps-with-the-aws-cdk-using-typescript.html
[47] https://dev.classmethod.jp/articles/developed-a-serverless-api-with-litestar-and-mangum/
[48] https://zenn.dev/jolly96k/articles/569cbd3c665023
[49] https://tech.basicinc.jp/articles/213
[50] https://blog.usize-tech.com/aws-cdk-construct/
[51] https://qiita.com/makky12/items/70a544e42f34841be5c7
[52] https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.SecurityGroup.html
[53] https://www.reddit.com/r/aws/comments/1du00po/seeking_advice_aws_cdk_vs_serverless_framework/
[54] https://qiita.com/tamabe/items/7f3c726723ba059f499f
[55] https://docs.astral.sh/uv/guides/integration/aws-lambda/
[56] https://dev.classmethod.jp/articles/aws-cdk-ec2-instance-os-conditional-branching/
[57] https://fixel.co.jp/blog/cdk-lambda-typescript
[58] https://dev.classmethod.jp/articles/cdk-existing-resource/
[59] https://www.nxted.co.jp/blog/blog_detail?id=122
[60] https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_lambda/README.html
[61] https://note.com/minato_kame/n/nff628b4c2f91
[62] https://zenn.dev/hayata_yamamoto/articles/781efca1687272
[63] https://zenn.dev/hikapoppin/articles/559cf40a50af7e
[64] https://www.reddit.com/r/aws/comments/13wi6sw/building_serverless_websites_lambdas_written_with/?tl=ja
[65] https://docs.aws.amazon.com/ja_jp/cdk/v2/guide/constructs.html
[66] https://aws.amazon.com/jp/builders-flash/202301/lambda-web-adapter/
[67] https://github.com/aws-samples/lambda-web-adapter-benchmark-sample
[68] https://dev.to/aws-builders/fastapi-with-aws-serverless-powered-by-cdk-typescript-58a1
[69] https://www.restack.io/p/deploying-chatbots-serverless-answer-cat-ai
[70] https://github.com/aws-samples/aws-cdk-l2-constructs
[71] https://qiita.com/1hakusai1/items/7ae0b4ae4a816b22cf25
[72] https://iret.media/73684
[73] https://github.com/Kludex/mangum
[74] https://qiita.com/araki-yzrh/items/985015b9e08978e95b16
[75] https://aws.amazon.com/jp/builders-flash/202304/api-development-sam-fastapi-mangum/
[76] https://qiita.com/nomikazu_x/items/e31eb31d7a02cd3a49db
[77] https://mangum.io/integrating-asgi-with-aws-lambda-for-serverless-applications/

---
Perplexity の Eliot より: pplx.ai/share

FastAPIアプリケーションでPyPIパッケージとローカルWHLファイルを同時にレイヤー化するCDK実装方法について解説します。主に`PythonLayerVersion`と`lambda.LayerVersion`を組み合わせるアプローチが有効です。

## ローカルWHLを含むレイヤー設定
CDKスタックで以下のように複数レイヤーを定義します：

```typescript
// PyPIパッケージ用レイヤー
const pypiLayer = new python.PythonLayerVersion(this, "PypiLayer", {
  entry: "src/layers/pypi",
  compatibleRuntimes: [lambda.Runtime.PYTHON_3_11],
});

// ローカルWHL用レイヤー
const whlLayer = new lambda.LayerVersion(this, "WhlLayer", {
  code: lambda.Code.fromAsset("src/layers/whl"),
  compatibleRuntimes: [lambda.Runtime.PYTHON_3_11],
  description: "Local WHL packages layer",
});
```

## ディレクトリ構造
```
src/
├── layers/
│   ├── pypi/
│   │   └── requirements.txt  # FastAPI,uvicornなど
│   └── whl/
│       ├── local_package1-0.1.0-py3-none-any.whl
│       └── local_package2-0.2.0-cp311-cp311-manylinux_2_28_x86_64.whl
└── app/
    ├── main.py
    └── run.sh
```

## Lambda関数設定
```typescript
const func = new lambda.Function(this, "FastApiFunction", {
  // ...他の設定
  layers: [
    pypiLayer,
    whlLayer,
    lambda.LayerVersion.fromLayerVersionArn(
      // Lambda Web Adapterレイヤー
    )
  ],
  environment: {
    PYTHONPATH: [
      "/opt/python",        // PyPIレイヤーパス
      "/opt/whl",          // WHLレイヤーパス
      "/opt/bootstrap"      // Web Adapterパス
    ].join(":"),
  }
});
```

## 注意点
1. **WHL互換性**：ローカルWHLファイルはLambdaの実行環境（Pythonバージョン、OS、アーキテクチャ）と互換性があることを確認[3][5]
2. **パス設定**：`PYTHONPATH`に両レイヤーのパスを明示的に追加
3. **レイヤー制限**：レイヤー合計サイズが250MBを超えないように管理[6]
4. **ビルド最適化**：WHLファイルは事前に`pip download --platform`で取得可能[2][8]

ARMアーキテクチャを使用する場合、WHLファイルが`manylinux2014_aarch64`用であることを確認し、CDKのバンドリング設定で適切なプラットフォームを指定します[8]。

Citations:
[1] https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/python-package.html
[2] https://repost.aws/ja/knowledge-center/lambda-python-package-compatible
[3] https://qiita.com/Bashi50/items/1f72a93dbde23de55dda
[4] https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/python-layers.html
[5] https://zenn.dev/ncdc/articles/30a777a515a921
[6] https://qiita.com/takmot/items/346ca1a0fd95737a4445
[7] https://qiita.com/_YukiOgawa/items/66832f704be1218b09c4
[8] https://zenn.dev/spectee/articles/spectee-aws-lambda-python-architecture
[9] https://zenn.dev/fujimoto/articles/8aa786a1fcdfca
[10] https://engineerblog.markerise.com/infrastructure/20250327_874/
[11] https://www.cdata.com/jp/blog/awslambdapython
[12] https://zenn.dev/panyoriokome/scraps/e51393cc4eb0ae
[13] https://dev.classmethod.jp/articles/aws-lambda-paramiko/
[14] https://blog.usize-tech.com/aws-cdk-python/
[15] https://docs.aws.amazon.com/ja_jp/mwaa/latest/userguide/working-dags-dependencies.html
[16] https://cloud5.jp/saitou-cdk-entry-handson/
[17] https://dev.classmethod.jp/articles/cdk-glue-python-shell-custom-functions/

---
Perplexity の Eliot より: pplx.ai/share