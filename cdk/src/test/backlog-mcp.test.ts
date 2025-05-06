import { App } from 'aws-cdk-lib';
import { Template, Match } from 'aws-cdk-lib/assertions';
import { BacklogMcpStack } from '../lib/backlog-mcp-stack';

describe('BacklogMcpStack', () => {
  // 各環境ごとのテスト
  describe.each(['dev', 'stg', 'prod'])('Environment: %s', (environment) => {
    const app = new App();
    const stack = new BacklogMcpStack(app, `TestStack-${environment}`, {
      environment,
      alertEmail: environment === 'prod' ? 'admin@example.com' : undefined
    });
    const template = Template.fromStack(stack);

    test('Lambda Function with Web Adapter Created', () => {
      // 環境ごとに異なるメモリサイズを検証
      const expectedMemorySize = 
        environment === 'dev' ? 512 :
        environment === 'stg' ? 1024 : 2048;

      template.hasResourceProperties('AWS::Lambda::Function', {
        MemorySize: expectedMemorySize,
        Timeout: 30,
        Environment: {
          Variables: {
            TZ: 'Asia/Tokyo',
            NODE_ENV: environment,
            LOG_LEVEL: environment === 'prod' ? 'info' : 'debug'
          },
        },
      });

      // プロビジョンド同時実行数の検証（本番環境のみ）
      if (environment === 'prod') {
        template.hasResourceProperties('AWS::Lambda::Version', {
          ProvisionedConcurrentExecutions: 10
        });
      }
    });

    test('API Gateway REST API Created', () => {
      template.hasResourceProperties('AWS::ApiGateway::RestApi', {
        Name: Match.stringLikeRegexp(`backlog-mcp-${environment}-api`),
        Description: Match.stringLikeRegexp(`API for Backlog Model Context Protocol \\(${environment}\\)`),
      });

      // デプロイメント設定の検証
      template.hasResourceProperties('AWS::ApiGateway::Stage', {
        StageName: environment,
        TracingEnabled: true,
        MethodSettings: Match.arrayWith([
          Match.objectLike({
            LoggingLevel: 'INFO',
            MetricsEnabled: true,
            DataTraceEnabled: environment !== 'prod'
          })
        ])
      });
    });

    test('Usage Plan with API Key Created', () => {
      // 環境ごとに異なるレート制限を検証
      const expectedRateLimit = 
        environment === 'dev' ? 50 :
        environment === 'stg' ? 100 : 500;
      
      const expectedBurstLimit = 
        environment === 'dev' ? 25 :
        environment === 'stg' ? 50 : 100;
      
      const expectedQuotaLimit = 
        environment === 'dev' ? 5000 :
        environment === 'stg' ? 10000 : 1000000;

      template.hasResourceProperties('AWS::ApiGateway::UsagePlan', {
        Name: Match.stringLikeRegexp(`${environment}-standard`),
        Throttle: {
          RateLimit: expectedRateLimit,
          BurstLimit: expectedBurstLimit,
        },
        Quota: {
          Limit: expectedQuotaLimit,
          Period: 'MONTH',
        }
      });

      template.hasResourceProperties('AWS::ApiGateway::ApiKey', {
        Description: Match.stringLikeRegexp(`API Key for Backlog MCP \\(${environment}\\)`),
        Enabled: true,
      });
    });

    test('CloudFront Distribution with Security Headers Created', () => {
      // 環境ごとに異なるキャッシュTTLを検証
      const expectedCacheTtl = 
        environment === 'dev' ? 5 :
        environment === 'stg' ? 10 : 30;

      template.hasResourceProperties('AWS::CloudFront::Distribution', {
        DistributionConfig: {
          DefaultCacheBehavior: {
            ViewerProtocolPolicy: 'https-only',
            AllowedMethods: ['GET', 'HEAD', 'OPTIONS', 'PUT', 'PATCH', 'POST', 'DELETE'],
            CachedMethods: ['GET', 'HEAD', 'OPTIONS'],
          },
          Comment: Match.stringLikeRegexp(`Backlog MCP API Distribution \\(${environment}\\)`),
          Enabled: true,
          PriceClass: environment === 'prod' ? 'PriceClass_All' : 'PriceClass_100',
          Logging: Match.objectLike({
            Enabled: true,
            IncludeCookies: false
          })
        },
      });

      template.hasResourceProperties('AWS::CloudFront::CachePolicy', {
        CachePolicyConfig: {
          DefaultTTL: expectedCacheTtl,
          MaxTTL: expectedCacheTtl * 3,
          MinTTL: 0,
          ParametersInCacheKeyAndForwardedToOrigin: {
            EnableAcceptEncodingBrotli: true,
            EnableAcceptEncodingGzip: true
          }
        }
      });

      template.hasResourceProperties('AWS::CloudFront::ResponseHeadersPolicy', {
        ResponseHeadersPolicyConfig: {
          SecurityHeadersConfig: {
            StrictTransportSecurity: {
              AccessControlMaxAgeSec: 63072000,
              IncludeSubdomains: true,
              Override: true,
              Preload: true,
            },
            ContentTypeOptions: {
              Override: true,
            },
            FrameOptions: {
              FrameOption: 'DENY',
              Override: true,
            },
            XSSProtection: {
              Protection: true,
              ModeBlock: true,
              Override: true,
            },
          },
        },
      });
    });

    // WAF設定のテスト（stgとprodのみ）
    if (environment === 'stg' || environment === 'prod') {
      test('WAF Web ACL Created', () => {
        template.hasResourceProperties('AWS::WAFv2::WebACL', {
          Name: Match.stringLikeRegexp(`backlog-mcp-${environment}-web-acl`),
          Scope: 'CLOUDFRONT',
          DefaultAction: {
            Allow: {}
          },
          Rules: Match.arrayWith([
            Match.objectLike({
              Name: 'SQLInjectionRule',
              Priority: 10
            }),
            Match.objectLike({
              Name: 'RateLimitRule',
              Priority: 20,
              Action: {
                Block: {}
              }
            })
          ])
        });
      });
    }

    // アラーム設定のテスト（prodのみ）
    if (environment === 'prod') {
      test('CloudWatch Alarms Created', () => {
        // SNSトピック
        template.hasResourceProperties('AWS::SNS::Topic', {
          TopicName: Match.stringLikeRegexp(`backlog-mcp-${environment}-alarms`)
        });

        // メール通知
        template.hasResourceProperties('AWS::SNS::Subscription', {
          Protocol: 'email',
          Endpoint: 'admin@example.com'
        });

        // Lambda関数のエラーアラーム
        template.hasResourceProperties('AWS::CloudWatch::Alarm', {
          AlarmName: Match.stringLikeRegexp(`backlog-mcp-${environment}-lambda-errors`),
          Threshold: 1,
          EvaluationPeriods: 3,
          ComparisonOperator: 'GreaterThanThreshold'
        });

        // API Gatewayの5xxエラーアラーム
        template.hasResourceProperties('AWS::CloudWatch::Alarm', {
          AlarmName: Match.stringLikeRegexp(`backlog-mcp-${environment}-api-5xx-errors`),
          Threshold: 1,
          EvaluationPeriods: 3,
          ComparisonOperator: 'GreaterThanThreshold'
        });
      });
    }

    // IAMポリシーのテスト
    test('IAM Minimal Permissions Policy Created', () => {
      template.hasResourceProperties('AWS::IAM::Policy', {
        PolicyDocument: {
          Statement: Match.arrayWith([
            Match.objectLike({
              Effect: 'Allow',
              Action: [
                'logs:CreateLogGroup',
                'logs:CreateLogStream',
                'logs:PutLogEvents'
              ],
              Resource: Match.stringLikeRegexp(`arn:aws:logs:.*:.*:log-group:/aws/lambda/backlog-mcp-${environment}-function:.*`)
            }),
            Match.objectLike({
              Effect: 'Allow',
              Action: [
                'xray:PutTraceSegments',
                'xray:PutTelemetryRecords'
              ],
              Resource: ['*']
            })
          ])
        }
      });
    });

    // CloudWatch Logsのテスト
    test('CloudWatch Logs Group Created', () => {
      template.hasResourceProperties('AWS::Logs::LogGroup', {
        LogGroupName: Match.stringLikeRegexp(`/aws/lambda/backlog-mcp-${environment}-function`),
        RetentionInDays: environment === 'prod' ? 30 : 14
      });
    });

    // 出力値のテスト
    test('Stack Outputs Created', () => {
      template.hasOutput('Environment', {
        Value: environment
      });

      template.hasOutput('ApiGatewayUrl', {
        Description: 'API Gateway endpoint URL',
        Export: {
          Name: Match.stringLikeRegexp(`backlog-mcp-${environment}-api-url`)
        }
      });

      template.hasOutput('CloudFrontDomain', {
        Description: 'CloudFront distribution domain name',
        Export: {
          Name: Match.stringLikeRegexp(`backlog-mcp-${environment}-cloudfront-domain`)
        }
      });

      template.hasOutput('ApiKeyId', {
        Description: 'API Key ID',
        Export: {
          Name: Match.stringLikeRegexp(`backlog-mcp-${environment}-api-key-id`)
        }
      });
    });
  });
});
