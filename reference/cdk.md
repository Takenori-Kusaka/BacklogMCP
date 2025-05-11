# AWS CDK TypeScriptプロジェクトの基本構成と構築手順

AWS Cloud Development Kit (CDK)でTypeScriptプロジェクトを始める際の基本的な構成と手順をまとめました。この手順書では、初めてCDKを使う方向けに、プロジェクトのセットアップからビルド・デプロイまでの流れを説明します。

## 1. 前提条件

以下のツールをインストールしておく必要があります：

- Node.js (v14.15.0以上、LTSバージョン推奨)[7][16]
- npm (Node.jsとともにインストールされます)
- AWS CLI v2[16]
- AWSアカウントと認証情報の設定[16]
- TypeScriptコンパイラ[1][7]

```bash
# TypeScriptのインストール
npm install -g typescript
# AWS CDK Toolkitのインストール
npm install -g aws-cdk
```

## 2. CDKプロジェクトの作成

### 方法1: CDK CLIを使ったプロジェクト作成（推奨）

```bash
# 新しいディレクトリを作成し、そこに移動
mkdir my-cdk-project
cd my-cdk-project

# CDKプロジェクトの初期化（TypeScript形式）
cdk init app --language typescript
```

このコマンドは必要なファイルとフォルダ構造を自動的に作成します[1][10][16]。

### 方法2: プロジェクトを手動で作成

空のディレクトリから始める場合は以下の手順で[8][14]：

```bash
# 新しいディレクトリを作成し、そこに移動
mkdir my-cdk-project
cd my-cdk-project

# npmプロジェクトの初期化
npm init -y

# 必要なパッケージのインストール
npm install -D aws-cdk aws-cdk-lib constructs typescript ts-node @types/node

# 基本的なディレクトリ構造の作成
mkdir bin lib

# TypeScript設定ファイルの作成
tsc --init
# tsconfig.jsonを編集して、targetをES2020に設定

# cdk.jsonファイルの作成
echo '{ "app": "npx ts-node bin/my-cdk-project.ts" }' > cdk.json
```

## 3. プロジェクトの標準的なファイル構造

CDKプロジェクトの標準的なファイル構造は以下のようになります[2][7][8]：

```
my-cdk-project/
├── bin/
│   └── my-cdk-project.ts     # アプリケーションのエントリーポイント
├── lib/
│   └── my-cdk-project-stack.ts  # スタック定義
├── test/                    # テストコード
├── cdk.json                 # CDK設定ファイル
├── package.json             # npm設定
├── package-lock.json
└── tsconfig.json            # TypeScript設定
```

## 4. tsconfig.jsonの基本設定

TypeScriptプロジェクトでは、`tsconfig.json`ファイルがコンパイラの設定を定義します[4][7]：

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["es2020"],
    "declaration": true,
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": false,
    "inlineSourceMap": true,
    "inlineSources": true,
    "experimentalDecorators": true,
    "strictPropertyInitialization": false,
    "typeRoots": ["./node_modules/@types"]
  },
  "exclude": ["node_modules", "cdk.out"]
}
```

## 5. package.jsonの基本設定

典型的なCDKプロジェクトの`package.json`は以下のようになります[7]：

```json
{
  "name": "my-cdk-project",
  "version": "0.1.0",
  "bin": {
    "my-cdk-project": "bin/my-cdk-project.js"
  },
  "scripts": {
    "build": "tsc",
    "watch": "tsc -w",
    "test": "jest",
    "cdk": "cdk"
  },
  "devDependencies": {
    "@types/jest": "^26.0.10",
    "@types/node": "10.17.27",
    "jest": "^26.4.2",
    "ts-jest": "^26.2.0",
    "aws-cdk": "2.16.0",
    "ts-node": "^9.0.0",
    "typescript": "~3.9.7"
  },
  "dependencies": {
    "aws-cdk-lib": "2.16.0",
    "constructs": "^10.0.0",
    "source-map-support": "^0.5.16"
  }
}
```

## 6. 基本的なスタック定義

`lib/my-cdk-project-stack.ts`ファイルにスタック定義を記述します[2][4]：

```typescript
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class MyCdkProjectStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // ここにリソース定義を追加
    // 例: S3バケットの作成
    new cdk.aws_s3.Bucket(this, 'MyFirstBucket', {
      versioned: true,
    });
  }
}
```

## 7. アプリケーションのエントリーポイント

`bin/my-cdk-project.ts`ファイルはアプリケーションのエントリーポイントです[2][8]：

```typescript
#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { MyCdkProjectStack } from '../lib/my-cdk-project-stack';

const app = new cdk.App();
new MyCdkProjectStack(app, 'MyCdkProjectStack');
```

## 8. ビルドとデプロイの手順

### ビルド手順

CDKプロジェクトでは、通常以下の手順でビルドを行います[1][4][7]：

```bash
# プロジェクトのルートディレクトリで実行
npm run build
```

このコマンドは実際には`package.json`の`scripts`セクションで定義された`tsc`コマンドを実行し、TypeScriptコードをJavaScriptにコンパイルします。

**注意点**:
- `npm run build`はプロジェクトのルートディレクトリで実行する必要があります
- エラーが発生した場合は、`tsconfig.json`の設定を確認してください
- TypeScriptのバージョンの不一致が原因でエラーが発生することもあります[14]

### CloudFormationテンプレートの合成

ビルド後、以下のコマンドでCloudFormationテンプレートを生成できます[15][16]：

```bash
cdk synth
```

### スタックのデプロイ

初めてCDKを使用する場合は、最初に`bootstrap`コマンドを実行してデプロイに必要なリソースを準備する必要があります[12][15][16]：

```bash
# 最初に一度だけ実行（アカウント/リージョンごとに必要）
cdk bootstrap

# スタックのデプロイ
cdk deploy
```

## 9. よく使うCDKコマンド一覧

CDKプロジェクトで頻繁に使用するコマンドは以下の通りです[11][15][16]：

```bash
cdk init app --language typescript  # プロジェクトの初期化
cdk bootstrap                       # デプロイ環境の準備
cdk ls                              # スタック一覧の表示
cdk synth                           # CloudFormationテンプレートの生成
cdk diff                            # デプロイ済みスタックとの差分表示
cdk deploy                          # スタックのデプロイ
cdk destroy                         # スタックの削除
```

## 10. コンテキスト変数の使用（オプション）

コンテキスト変数を使用すると、環境によって異なる値を設定できます[3]：

```bash
# コマンドラインでコンテキスト変数を指定
cdk synth -c bucket_name=mygroovybucket
```

または`cdk.json`ファイルに定義：

```json
{
  "app": "npx ts-node bin/my-cdk-project.ts",
  "context": {
    "bucket_name": "myotherbucket"
  }
}
```

アプリケーションコード内でのコンテキスト変数の取得：

```typescript
const bucketName = this.node.tryGetContext('bucket_name');
```

## 11. Lambda関数を含むプロジェクト（オプション）

Lambda関数をTypeScriptで実装する場合、専用の`tsconfig.json`が必要になることがあります[4][6]：

```bash
# プロジェクト構造の例
my-cdk-project/
├── lambda/
│   ├── src/
│   │   └── index.ts    # Lambda関数のソースコード
│   └── tsconfig.json   # Lambda用のTypeScript設定
└── ...
```

Lambda関数用の`tsconfig.json`の例[6]：

```json
{
  "extends": "../../tsconfig.json",
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "node",
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true
  }
}
```

## トラブルシューティング

- **ビルドエラー**: `tsconfig.json`の設定が正しいか確認してください
- **パッケージの互換性エラー**: CDKライブラリのバージョンが一致しているか確認[14]
- **コンパイルエラー**: TypeScriptのバージョンが3.8以上か確認[1][7]
- **デプロイエラー**: `cdk bootstrap`を実行済みか確認[15][16]

このガイドを参考に、AWS CDKプロジェクトの構築と管理が円滑に進むことを願っています。

Citations:
[1] https://docs.aws.amazon.com/ja_jp/cdk/v2/guide/work-with-cdk-typescript.html
[2] https://www.restack.io/p/aws-cdk-answer-project-structure-typescript
[3] https://docs.aws.amazon.com/ja_jp/cdk/v2/guide/get_context_var.html
[4] https://qiita.com/takmot/items/83326c5e3e3213038dde
[5] https://docs.aws.amazon.com/ja_jp/cdk/v2/guide/cli.html
[6] https://www.cloudbuilders.jp/articles/4642/
[7] https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-typescript.html
[8] https://persol-serverworks.co.jp/blog/cdk/cdk-typescript-1kara.html
[9] https://docs.aws.amazon.com/ja_jp/cdk/v2/guide/ref-cli-cmd.html
[10] https://zenn.dev/ufoo68/books/3fbd1969bd4b21c5454b/viewer/cdkinit
[11] https://dev.classmethod.jp/articles/aws-cdk-command-line-interface/
[12] https://docs.aws.amazon.com/ja_jp/cdk/v2/guide/hello-world.html
[13] https://zenn.dev/mjxo/articles/cb3cb6fc2daee5
[14] https://dev.classmethod.jp/articles/aws-cdk-getting-started-101/
[15] https://dev.classmethod.jp/articles/cdk-practice-30-cdk-command/
[16] https://tech-blog.cloud-config.jp/2023-06-26-aws-cdk-command-hands-on
[17] https://zenn.dev/murakami_koki/articles/81c0bcba772428
[18] https://www.youtube.com/watch?v=HpUZvO-JDxI
[19] https://zenn.dev/mn87/articles/dcd99734b8bb05
[20] https://dev.classmethod.jp/articles/cdk-typescript-absolute-path-import/
[21] https://qiita.com/0xmks/items/80f593d34fd6107d34dd
[22] https://docs.aws.amazon.com/cdk/v2/guide/projects.html
[23] https://docs.aws.amazon.com/ja_jp/cdk/v2/guide/cli.html
[24] https://www.cloudbuilders.jp/articles/4642/
[25] https://techblog.asia-quest.jp/202501/intern-builds-cdk-environment-with-typescript
[26] https://zenn.dev/masaino/articles/c9d4a7ebce535e
[27] https://dev.classmethod.jp/articles/aws-cdk-multi-environment-config/
[28] https://github.com/aws-samples/aws-cdk-examples/blob/main/typescript/ecs/ecs-service-with-advanced-alb-config/tsconfig.json
[29] https://qiita.com/marumeru/items/22882d4a1d524eec1788
[30] https://pages.awscloud.com/rs/112-TZM-766/images/AWS-Black-Belt_2023_AWS-CDK-Basic-3-AppDev_0831_v1.pdf
[31] https://qiita.com/ymgc3/items/dac4615a29af4c6d4d37
[32] https://dev.classmethod.jp/articles/cdk-practice-26-version-2/
[33] https://qiita.com/masatomix/items/8fc3d52ee89489967c09
[34] https://docs.aws.amazon.com/ja_jp/cdk/v2/guide/hello_world.html
[35] https://qiita.com/yuma_haga/items/56490cbab1cf54d619e5
[36] https://zenn.dev/mo_ri_regen/articles/aws-cdk-command
[37] https://docs.aws.amazon.com/ja_jp/cdk/v2/guide/work-with-cdk-typescript.html
[38] https://qiita.com/tsurupoyo/items/f30ac4e8d2047c4edbe4

---
Perplexity の Eliot より: pplx.ai/share