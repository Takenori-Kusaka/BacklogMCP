import * as cdk from 'aws-cdk-lib';
import { Template, Match } from 'aws-cdk-lib/assertions';
import { BacklogMcpStack } from '../lib/backlog-mcp-stack';
import { describe, test, expect } from '@jest/globals';

describe('BacklogMcpStack', () => {
  // 環境ごとのテスト
  describe('環境別設定テスト', () => {
    test('dev環境のスタックが正しく作成される', () => {
      // ARRANGE
      const app = new cdk.App();
      const stack = new BacklogMcpStack(app, 'TestStack', {
        environment: 'dev',
      });

      // ACT
      const template = Template.fromStack(stack);

      // ASSERT
      // Lambda関数が作成されていることを確認
      template.hasResourceProperties('AWS::Lambda::Function', {
        FunctionName: 'backlog-mcp-dev-function',
        MemorySize: 512,
        Timeout: 30,
        Environment: {
          Variables: {
            TZ: 'Asia/Tokyo',
            NODE_ENV: 'dev',
            LOG_LEVEL: 'debug',
          },
        },
      });

      // API Gatewayが作成されていることを確認
      template.hasResourceProperties('AWS::ApiGateway::RestApi', {
        Name: 'backlog-mcp-dev-api',
      });

      // UsagePlanが作成されていることを確認
      template.hasResourceProperties('AWS::ApiGateway::UsagePlan', {
        Throttle: {
          RateLimit: 50,
          BurstLimit: 25,
        },
        Quota: {
          Limit: 5000,
          Period: 'MONTH',
        },
      });

      // CloudFrontが作成されていることを確認
      template.hasResourceProperties('AWS::CloudFront::Distribution', {
        DistributionConfig: {
          Enabled: true,
          PriceClass: 'PriceClass_100',
        },
      });

      // WAFが作成されていないことを確認（dev環境では作成されない）
      template.resourceCountIs('AWS::WAFv2::WebACL', 0);

      // CloudWatch Alarmsが作成されていないことを確認（dev環境では作成されない）
      template.resourceCountIs('AWS::CloudWatch::Alarm', 0);
    });

    test('stg環境のスタックが正しく作成される', () => {
      // ARRANGE
      const app = new cdk.App();
      const stack = new BacklogMcpStack(app, 'TestStack', {
        environment: 'stg',
      });

      // ACT
      const template = Template.fromStack(stack);

      // ASSERT
      // Lambda関数が作成されていることを確認
      template.hasResourceProperties('AWS::Lambda::Function', {
        FunctionName: 'backlog-mcp-stg-function',
        MemorySize: 1024,
        Timeout: 30,
        Environment: {
          Variables: {
            TZ: 'Asia/Tokyo',
            NODE_ENV: 'stg',
            LOG_LEVEL: 'debug',
          },
        },
      });

      // API Gatewayが作成されていることを確認
      template.hasResourceProperties('AWS::ApiGateway::RestApi', {
        Name: 'backlog-mcp-stg-api',
      });

      // UsagePlanが作成されていることを確認
      template.hasResourceProperties('AWS::ApiGateway::UsagePlan', {
        Throttle: {
          RateLimit: 100,
          BurstLimit: 50,
        },
        Quota: {
          Limit: 10000,
          Period: 'MONTH',
        },
      });

      // CloudFrontが作成されていることを確認
      template.hasResourceProperties('AWS::CloudFront::Distribution', {
        DistributionConfig: {
          Enabled: true,
          PriceClass: 'PriceClass_100',
        },
      });

      // WAFが作成されていることを確認（stg環境では作成される）
      template.hasResourceProperties('AWS::WAFv2::WebACL', {
        Name: 'backlog-mcp-stg-web-acl',
        Scope: 'CLOUDFRONT',
      });

      // CloudWatch Alarmsが作成されていないことを確認（stg環境では作成されない）
      template.resourceCountIs('AWS::CloudWatch::Alarm', 0);
    });

    test('prod環境のスタックが正しく作成される', () => {
      // ARRANGE
      const app = new cdk.App();
      const stack = new BacklogMcpStack(app, 'TestStack', {
        environment: 'prod',
        alertEmail: 'alert@example.com',
      });

      // ACT
      const template = Template.fromStack(stack);

      // ASSERT
      // Lambda関数が作成されていることを確認
      template.hasResourceProperties('AWS::Lambda::Function', {
        FunctionName: 'backlog-mcp-prod-function',
        MemorySize: 2048,
        Timeout: 30,
        Environment: {
          Variables: {
            TZ: 'Asia/Tokyo',
            NODE_ENV: 'prod',
            LOG_LEVEL: 'info',
          },
        },
      });

      // API Gatewayが作成されていることを確認
      template.hasResourceProperties('AWS::ApiGateway::RestApi', {
        Name: 'backlog-mcp-prod-api',
      });

      // UsagePlanが作成されていることを確認
      template.hasResourceProperties('AWS::ApiGateway::UsagePlan', {
        Throttle: {
          RateLimit: 500,
          BurstLimit: 100,
        },
        Quota: {
          Limit: 1000000,
          Period: 'MONTH',
        },
      });

      // CloudFrontが作成されていることを確認
      template.hasResourceProperties('AWS::CloudFront::Distribution', {
        DistributionConfig: {
          Enabled: true,
          PriceClass: 'PriceClass_All',
        },
      });

      // WAFが作成されていることを確認（prod環境では作成される）
      template.hasResourceProperties('AWS::WAFv2::WebACL', {
        Name: 'backlog-mcp-prod-web-acl',
        Scope: 'CLOUDFRONT',
      });

      // CloudWatch Alarmsが作成されていることを確認（prod環境では作成される）
      template.hasResourceProperties('AWS::CloudWatch::Alarm', {
        AlarmName: 'backlog-mcp-prod-lambda-errors',
      });

      template.hasResourceProperties('AWS::CloudWatch::Alarm', {
        AlarmName: 'backlog-mcp-prod-api-5xx-errors',
      });

      // SNS Topicが作成されていることを確認
      template.hasResourceProperties('AWS::SNS::Topic', {
        TopicName: 'backlog-mcp-prod-alarms',
      });

      // SNS Subscriptionが作成されていることを確認
      template.hasResourceProperties('AWS::SNS::Subscription', {
        Protocol: 'email',
        Endpoint: 'alert@example.com',
      });
    });
  });

  // リソース作成テスト
  describe('リソース作成テスト', () => {
    test('必要なリソースが全て作成される', () => {
      // ARRANGE
      const app = new cdk.App();
      const stack = new BacklogMcpStack(app, 'TestStack', {
        environment: 'dev',
      });

      // ACT
      const template = Template.fromStack(stack);

      // ASSERT
      // 必要なリソースが作成されていることを確認
      template.resourceCountIs('AWS::Lambda::Function', 1);
      template.resourceCountIs('AWS::ApiGateway::RestApi', 1);
      template.resourceCountIs('AWS::ApiGateway::UsagePlan', 1);
      template.resourceCountIs('AWS::ApiGateway::ApiKey', 1);
      template.resourceCountIs('AWS::CloudFront::Distribution', 1);
      template.resourceCountIs('AWS::CloudFront::ResponseHeadersPolicy', 1);
      template.resourceCountIs('AWS::CloudFront::CachePolicy', 1);
      template.resourceCountIs('AWS::IAM::Role', 2);
      // AWS::IAM::Policyリソースの数を確認
      template.resourceCountIs('AWS::IAM::Policy', 2);
      template.resourceCountIs('AWS::Logs::LogGroup', 1);
    });
  });

  // API Gateway設定テスト
  describe('API Gateway設定テスト', () => {
    test('API Gatewayに必要なリソースとメソッドが作成される', () => {
      // ARRANGE
      const app = new cdk.App();
      const stack = new BacklogMcpStack(app, 'TestStack', {
        environment: 'dev',
      });

      // ACT
      const template = Template.fromStack(stack);

      // ASSERT
      // APIリソースが作成されていることを確認
      template.hasResourceProperties('AWS::ApiGateway::Resource', {
        PathPart: 'api',
      });

      // v1リソースが作成されていることを確認
      template.hasResourceProperties('AWS::ApiGateway::Resource', {
        PathPart: 'v1',
      });

      // issuesリソースが作成されていることを確認
      template.hasResourceProperties('AWS::ApiGateway::Resource', {
        PathPart: 'issues',
      });

      // projectsリソースが作成されていることを確認
      template.hasResourceProperties('AWS::ApiGateway::Resource', {
        PathPart: 'projects',
      });

      // bulkリソースが作成されていることを確認
      template.hasResourceProperties('AWS::ApiGateway::Resource', {
        PathPart: 'bulk',
      });

      // GETメソッドが作成されていることを確認
      template.hasResourceProperties('AWS::ApiGateway::Method', {
        HttpMethod: 'GET',
        ApiKeyRequired: true,
      });

      // POSTメソッドが作成されていることを確認
      template.hasResourceProperties('AWS::ApiGateway::Method', {
        HttpMethod: 'POST',
        ApiKeyRequired: true,
      });
    });
  });

  // CloudFront設定テスト
  describe('CloudFront設定テスト', () => {
    test('CloudFrontに必要な設定が適用される', () => {
      // ARRANGE
      const app = new cdk.App();
      const stack = new BacklogMcpStack(app, 'TestStack', {
        environment: 'dev',
      });

      // ACT
      const template = Template.fromStack(stack);

      // ASSERT
      // CloudFrontディストリビューションが作成されていることを確認
      template.hasResourceProperties('AWS::CloudFront::Distribution', {
        DistributionConfig: {
          DefaultCacheBehavior: {
            ViewerProtocolPolicy: 'https-only',
            AllowedMethods: ['GET', 'HEAD', 'OPTIONS', 'PUT', 'PATCH', 'POST', 'DELETE'],
            CachedMethods: ['GET', 'HEAD', 'OPTIONS'],
          },
          Enabled: true,
          HttpVersion: Match.anyValue(),
          IPV6Enabled: Match.anyValue(),
          PriceClass: 'PriceClass_100',
        },
      });

      // レスポンスヘッダーポリシーが作成されていることを確認
      template.hasResourceProperties('AWS::CloudFront::ResponseHeadersPolicy', {
        ResponseHeadersPolicyConfig: {
          Name: Match.stringLikeRegexp('.*security-headers'),
          SecurityHeadersConfig: {
            ContentTypeOptions: {
              Override: true,
            },
            FrameOptions: {
              FrameOption: 'DENY',
              Override: true,
            },
            ReferrerPolicy: {
              ReferrerPolicy: 'same-origin',
              Override: true,
            },
            StrictTransportSecurity: {
              AccessControlMaxAgeSec: 63072000,
              IncludeSubdomains: true,
              Override: true,
              Preload: true,
            },
            XSSProtection: {
              ModeBlock: true,
              Override: true,
              Protection: true,
            },
          },
        },
      });
    });
  });

  // スナップショットテストは省略
  // CI環境ではスナップショットの更新が難しいため
});
