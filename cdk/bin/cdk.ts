#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
// import { Construct } from 'constructs'; // MyMinimalStackで使用していたが、元に戻すためコメントアウト

// --- ここから最小構成のスタック定義（削除） ---
// class MyMinimalStack extends cdk.Stack {
//   constructor(scope: Construct, id: string, props?: cdk.StackProps) {
//     super(scope, id, props);
//     // 最小限のリソースとしてS3バケットを定義
//     new cdk.aws_s3.Bucket(this, 'MyMinimalBucket');
//   }
// }
//
// const app = new cdk.App(); // BacklogMcpStackのappインスタンスで上書きされるためコメントアウト
// new MyMinimalStack(app, 'MyMinimalTestStack');
// app.synth(); // MyMinimalStackで使用していたが、元に戻すためコメントアウト
// --- ここまで最小構成のスタック定義（削除） ---

// --- ここから元のコード（コメントアウト解除） ---
import { BacklogMcpStack } from '../lib/backlog-mcp-stack';

const app = new cdk.App();

// 環境変数から取得するか、コンテキストから取得
const environment = app.node.tryGetContext('environment') || process.env.ENVIRONMENT || 'dev';
const alertEmail = app.node.tryGetContext('alertEmail') || process.env.ALERT_EMAIL;

// 共通のスタックパラメータ
const commonProps = {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'ap-northeast-1',
  },
  environment,
  alertEmail
};

// スタック名に環境名を含める
const stackName = `BacklogMcpStack-${environment}`;

// スタックの作成
new BacklogMcpStack(app, stackName, commonProps);

// タグの追加
cdk.Tags.of(app).add('Environment', environment);
cdk.Tags.of(app).add('Project', 'BacklogMCP');
cdk.Tags.of(app).add('ManagedBy', 'CDK');
// --- ここまで元のコード（コメントアウト解除） ---
