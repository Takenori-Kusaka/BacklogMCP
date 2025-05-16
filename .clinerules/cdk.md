# AWS CDKプロジェクト開発のための包括的ベストプラクティス集

## 命名規則とリソース管理
### リソース命名体系
{system}-{env}-{任意文字列}形式を基本構造とし、S3バケットには末尾にAWSアカウントIDを付与[2]。命名時には各サービス毎の最大文字数制限を厳守（例：IAMロール64文字、Lambda関数64文字）[2]。動的命名には`cdk.PhysicalName.GENERATE_IF_NEEDED`を活用し、CloudFormationの自動命名機能を優先[14]。

### 物理名vs論理名
ステートフルリソース（RDS/S3等）には明示的な物理名を割り当て、ステートレスリソースには自動生成名を使用[18]。論理IDの変更による意図しないリソース削除を防ぐため、`overrideLogicalId`メソッドの使用は極力回避[5]。

## プロジェクト構造設計
### ディレクトリ構成戦略
```
lib/
├── constructs/        # 再利用可能なL2/L3コンストラクト
├── stacks/            # 環境固有のスタック定義
├── types/             # 共通インターフェース型定義
└── utils/             # ヘルパー関数・ユーティリティ
test/
├── integration/       # 統合テスト
├── unit/              # ユニットテスト
└── snapshot/          # スナップショットテスト
``` 
環境固有設定はcdk.jsonではなくTypeScriptで管理し、動的コンフィグ生成を推奨[3][18]。

### コンストラクト設計原則
L1コンストラクトは直接使用せず、ビジネスロジックをカプセル化したL3コンストラクトを開発[11]。共通機能は抽象コンストラクトとして実装し、プロジェクト横断で再利用[19]。

## テスト戦略
### テストピラミッド実装
```
// スナップショットテスト例
test('Template matches snapshot', () => {
  const stack = new MyStack(app, 'TestStack');
  const template = Template.fromStack(stack);
  expect(template.toJSON()).toMatchSnapshot();
});

// アサーションテスト例
test('Has EC2 instance with proper tags', () => {
  Template.fromStack(stack).hasResourceProperties('AWS::EC2::Instance', {
    Tags: Match.arrayWith([{ Key: 'Env', Value: 'prod' }])
  });
});
```
テストカバレッジ目標：リソース作成/更新/削除操作の100%カバー[17]。ステートフルリソースにはintegテストを必須化[5]。

## CI/CDパイプライン構築
### CDK Pipelines設計
```
const pipeline = new CodePipeline(this, 'Pipeline', {
  synth: new ShellStep('Synth', {
    input: CodePipelineSource.gitHub('org/repo', 'main'),
    commands: ['npm ci', 'npm run build', 'npx cdk synth']
  }),
  selfMutation: true,
  assetPublishingCodeBuildDefaults: {
    buildEnvironment: { privileged: true }
  }
});
```
本番環境デプロイ前には手動承認ゲートを設置[8]。パイプラインスタックとアプリケーションスタックを分離し、権限分離を実現[8]。

## セキュリティ対策
### cdk-nag統合
```
import { AwsSolutionsChecks } from 'cdk-nag';

const app = new App();
cdk.Aspects.of(app).add(new AwsSolutionsChecks());
```
HIPAA/NIST/PCI DSS準拠チェックをパイプラインに組み込み[12]。ルール違反はデプロイブロックし、例外申請には抑制コメントを義務化[9]。

## 環境管理
### マルチアカウント構成
```
environments/
├── dev/
│   ├── config.ts
│   └── stacks/
├── prod/
│   ├── config.ts
│   └── stacks/
└── shared/            # 共有リソース
```
AWS OrganizationsとCDK Bootstrapを連携し、アカウント毎のデプロイロールを設定[14]。環境変数はコンテキスト経由で注入[18]。

## モニタリングとロギング
### 統合モニタリング設定
```
declare const function: lambda.Function;
const metric = function.metricErrors();
new Alarm(this, 'LambdaErrors', {
  metric,
  threshold: 1,
  evaluationPeriods: 1
});
```
全ての運用リソースにCloudWatchアラームを自動設定[6]。ロググループの保持期間は環境別に設定（開発:7日、本番:365日）[16]。

## 依存関係管理
### コンストラクトバージョニング
```
{
  "dependencies": {
    "@aws-cdk/core": "2.89.0",
    "@aws-constructs/security": "^3.2.1"
  }
}
```
コンストラクトライブラリはSemVerで厳格管理[11]。CDK CLIバージョンはプロジェクト全体で統一[4]。

## ドキュメンテーション
### 自動ドキュメント生成
```
npx cdk-docs
```
APIドキュメントはTypeDocで自動生成し、Architecture Decision Records(ADR)をdocs/ディレクトリで管理[19]。主要設計判断はRFC形式で文書化[3]。

## 災害復旧策
### バックアップ戦略
```
new s3.Bucket(this, 'DataBucket', {
  versioned: true,
  lifecycleRules: [{
    transitions: [{
      storageClass: s3.StorageClass.GLACIER,
      transitionAfter: Duration.days(90)
    }]
  }]
});
```
クロスリージョンバックアップをAWS Backupで自動化[18]。RDSスナップショットは別アカウントに複製[14]。

## コスト管理
### コスト見積もり
```
new CfnBudget(this, 'Budget', {
  budget: {
    budgetType: 'COST',
    timeUnit: 'MONTHLY',
    budgetLimit: { amount: 1000, unit: 'USD' }
  }
});
```
Infracost統合でPR毎にコスト差分を表示[17]。開発環境は週末自動シャットダウンを実装[8]。

## パフォーマンス最適化
### キャッシュ戦略
```
new cloudfront.Distribution(this, 'Distribution', {
  defaultBehavior: {
    cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED
  }
});
```
CDK合成時にAssetハッシュを活用し、不要なアップロードを回避[14]。VPCフローログでネットワークパターンを分析[16].

Citations:
[1] https://docs.aws.amazon.com/ja_jp/cdk/v2/guide/best-practices.html
[2] https://qiita.com/rm0063vpedc15/items/296e7401ac715ffe8b4d
[3] https://speakerdeck.com/soso_15315/aws-cdkwo4-5nian-shi-tutetadorizhao-itazui-xin-gou-cheng
[4] https://qiita.com/watany/items/dbf6d6b56cd10e510b0e
[5] https://qiita.com/Nana_777/items/fa9f5074099f88ea35ba
[6] https://www.ctc-g.co.jp/solutions/cloud/column/article/96.html
[7] https://zenn.dev/hikapoppin/articles/ab39718866cbaf
[8] https://tech.quickguard.jp/posts/cdk-pipeline/
[9] https://zenn.dev/ncdc/articles/7aa0d9928689c4
[10] https://dev.classmethod.jp/articles/cline-context-model-guide/
[11] https://speakerdeck.com/konokenj/cdk-best-practice-2024
[12] https://aws.amazon.com/jp/blogs/news/manage-application-security-and-compliance-with-the-aws-cloud-development-kit-and-cdk-nag/
[13] https://dev.classmethod.jp/articles/cline-202504/
[14] https://aws.amazon.com/jp/blogs/news/best-practices-for-developing-cloud-applications-with-aws-cdk/
[15] https://www.ctc-g.co.jp/solutions/cloud/column/article/95.html
[16] https://zenn.dev/azunyan/articles/b3eb1fb2a9cc72
[17] https://qiita.com/konta74315/items/0f2d8b67c6cf214f6e06
[18] https://engineering.mobalab.net/2024/10/22/my-best-practices-for-aws-cdk/
[19] https://docs.aws.amazon.com/ja_jp/prescriptive-guidance/latest/best-practices-cdk-typescript-iac/development-best-practices.html
[20] https://qiita.com/Nana_777/items/fa9f5074099f88ea35ba
[21] https://dev.classmethod.jp/articles/best-way-to-name-aws-cdk-construct-id/
[22] https://speakerdeck.com/konokenj/cdk-best-practice-2024
[23] https://qiita.com/kentata19/items/b39f2fd85d3107b263ca
[24] https://docs.aws.amazon.com/ja_jp/prescriptive-guidance/latest/patterns/check-aws-cdk-applications-or-cloudformation-templates-for-best-practices-by-using-cdk-nag-rule-packs.html
[25] https://dev.to/aws-builders/how-to-publish-custom-cdk-nag-rules-and-rule-packs-with-projen-g1i
[26] https://qiita.com/tyskJ/items/5b3a954e51f6917d29b9
[27] https://aws.amazon.com/jp/blogs/news/aws-cdk-is-splitting-construct-library-and-cli/
[28] https://github.com/cdklabs/cdk-nag
[29] https://qiita.com/kiyoshi999/items/38a5c753f06d3e92934a
[30] https://zenn.dev/lea/articles/cafa94350d8d57
[31] https://dev.classmethod.jp/articles/aws-cdk-compliance-check-with-cdk-nag/
[32] https://qiita.com/asw_hoggge/items/45df2a39c285b823d73f
[33] https://zenn.dev/ozen/articles/8df070e85990ca
[34] https://zenn.dev/watany/articles/85af6cfb8dccb2
[35] https://speakerdeck.com/ryome/clinedeaws-cdkyainhuragou-cheng-tu-zuo-tutemita
[36] https://x.com/pahudnet/status/1892760518651216238
[37] https://zenn.dev/watany/articles/50665ee40f4948
[38] https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib-readme.html
[39] https://zenn.dev/acntechjp/articles/4c15c2a60fdacf

---
Perplexity の Eliot より: pplx.ai/share