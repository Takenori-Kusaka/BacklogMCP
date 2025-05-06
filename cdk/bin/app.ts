#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
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
