import { App } from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { BacklogMcpStack } from '../lib/backlog-mcp-stack';

describe('BacklogMcpStack', () => {
  const app = new App();
  const stack = new BacklogMcpStack(app, 'TestStack');
  const template = Template.fromStack(stack);

  test('Lambda Function with Web Adapter Created', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
      MemorySize: 1024,
      Timeout: 30,
      Environment: {
        Variables: {
          TZ: 'Asia/Tokyo',
        },
      },
    });
  });

  test('API Gateway REST API Created', () => {
    template.hasResourceProperties('AWS::ApiGateway::RestApi', {
      Name: 'Backlog MCP API',
      Description: 'API for Backlog Model Context Protocol',
    });
  });

  test('Usage Plan with API Key Created', () => {
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

    template.hasResourceProperties('AWS::ApiGateway::ApiKey', {
      Description: 'API Key for Backlog MCP',
      Enabled: true,
    });
  });

  test('CloudFront Distribution with Security Headers Created', () => {
    template.hasResourceProperties('AWS::CloudFront::Distribution', {
      DistributionConfig: {
        DefaultCacheBehavior: {
          ViewerProtocolPolicy: 'https-only',
          AllowedMethods: ['GET', 'HEAD', 'OPTIONS', 'PUT', 'PATCH', 'POST', 'DELETE'],
          CachedMethods: ['GET', 'HEAD', 'OPTIONS'],
          Compress: true,
        },
        Comment: 'Backlog MCP API Distribution',
        Enabled: true,
        HttpVersion: 'http2',
        IPV6Enabled: true,
      },
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
});
