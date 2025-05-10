#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { BacklogMcpStack } from '../lib/backlog-mcp-stack';

const app = new cdk.App();

// 環境変数から取得するか、コンテキストから取得
const environment = app.node.tryGetContext('environment') || process.env.ENVIRONMENT || 'dev';
const alertEmail = app.node.tryGetContext('alertEmail') || process.env.ALERT_EMAIL;

// スタック名に環境名を含める
const stackName = `BacklogMcpStack-${environment}`;

// スタックの作成
new BacklogMcpStack(app, stackName, {
  environment: environment,
  alertEmail: alertEmail,
  /* For environment-agnostic stacks, we don't specify 'env' so that the stack can be deployed anywhere.
   * For local debugging and testing, we don't need to specify AWS account and region. */
});

// タグの追加
cdk.Tags.of(app).add('Environment', environment);
cdk.Tags.of(app).add('Project', 'BacklogMCP');
cdk.Tags.of(app).add('ManagedBy', 'CDK');
