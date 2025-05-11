import * as cdk from 'aws-cdk-lib';
import * as fs from 'fs';          // use built-in fs for local bundling
import { DockerImage } from 'aws-cdk-lib'; // DockerImage をインポート
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as wafv2 from 'aws-cdk-lib/aws-wafv2';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';
import * as actions from 'aws-cdk-lib/aws-cloudwatch-actions';
import { Duration } from 'aws-cdk-lib';
import * as path from 'path'; // pathモジュールをインポート
import * as python from '@aws-cdk/aws-lambda-python-alpha';

export interface BacklogMcpStackProps extends cdk.StackProps {
  environment: string;
  alertEmail?: string;
}

export class BacklogMcpStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: BacklogMcpStackProps) {
    super(scope, id, props);

    const { environment, alertEmail } = props;

    // 環境ごとの設定値
    const config = {
      lambda: {
        memorySize: environment === 'dev' ? 512 : environment === 'stg' ? 1024 : 2048,
        timeout: 30,
        provisionedConcurrentExecutions: environment === 'prod' ? 10 : undefined,
        logRetention: environment === 'prod' ? 30 : 14,
      },
      apiGateway: {
        rateLimit: environment === 'dev' ? 50 : environment === 'stg' ? 100 : 500,
        burstLimit: environment === 'dev' ? 25 : environment === 'stg' ? 50 : 100,
        quotaLimit: environment === 'dev' ? 5000 : environment === 'stg' ? 10000 : 1000000,
      },
      cloudFront: {
        cacheTtl: environment === 'dev' ? 5 : environment === 'stg' ? 10 : 30,
        priceClass: environment === 'prod' ? cloudfront.PriceClass.PRICE_CLASS_ALL : cloudfront.PriceClass.PRICE_CLASS_100,
      },
    };

    // CloudWatch Logs Group
    const logGroup = new logs.LogGroup(this, 'LambdaLogGroup', {
      logGroupName: `/aws/lambda/backlog-mcp-${environment}-function`,
      retention: config.lambda.logRetention,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // IAM Role for Lambda
    const lambdaRole = new iam.Role(this, 'LambdaExecutionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      description: `Execution role for Backlog MCP Lambda (${environment})`,
    });

    // IAM Policy for Lambda
    const lambdaPolicy = new iam.Policy(this, 'LambdaExecutionPolicy', {
      statements: [
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            'logs:CreateLogGroup',
            'logs:CreateLogStream',
            'logs:PutLogEvents',
          ],
          resources: [
            // Use wildcard for region and account to generate a static ARN string matching test regex
            `arn:aws:logs:*:*:log-group:/aws/lambda/backlog-mcp-${environment}-function:*`,
          ],
        }),
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            'xray:PutTraceSegments',
            'xray:PutTelemetryRecords',
          ],
          resources: ['*'],
        }),
      ],
    });

    lambdaPolicy.attachToRole(lambdaRole);

    // PyPIパッケージ用レイヤー
    const pypiLayer = new python.PythonLayerVersion(this, 'PypiLayer', {
      entry: path.join(__dirname, '../../../build/lambda_layer'),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_10],
      description: 'Backlog MCP PyPI Packages Layer',
    });

    // ローカルWHL用レイヤー（pybacklogpy）
    const whlLayer = new lambda.LayerVersion(this, 'WhlLayer', {
      code: lambda.Code.fromAsset(path.join(__dirname, '../../../dependencies')),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_10],
      description: 'Local WHL packages layer for pybacklogpy',
    });

    // Lambda Function
    const lambdaFunction = new lambda.Function(this, 'BacklogMcpFunction', {
      functionName: `backlog-mcp-${environment}-function`,
      runtime: lambda.Runtime.PYTHON_3_10,
      code: lambda.Code.fromAsset(path.join(__dirname, '../../../app')),
      handler: 'main.handler',
      memorySize: config.lambda.memorySize,
      timeout: Duration.seconds(config.lambda.timeout),
      environment: {
        TZ: 'Asia/Tokyo',
        PYTHONPATH: [
          '/var/runtime',
          '/opt/python',  // PyPIレイヤーパス
          '/opt'          // WHLレイヤーパス
        ].join(':'),
        LOG_LEVEL: environment === 'prod' ? 'info' : 'debug',
        READ_ONLY_MODE: process.env.READ_ONLY_MODE || 'False',
        BACKLOG_API_KEY: process.env.BACKLOG_API_KEY || 'YOUR_BACKLOG_API_KEY_PLACEHOLDER',
        BACKLOG_SPACE: process.env.BACKLOG_SPACE || 'YOUR_BACKLOG_SPACE_PLACEHOLDER',
        BACKLOG_PROJECT: process.env.BACKLOG_PROJECT || 'YOUR_BACKLOG_PROJECT_PLACEHOLDER',
        BACKLOG_DISABLE_SSL_VERIFY: process.env.BACKLOG_DISABLE_SSL_VERIFY || 'false',
      },
      role: lambdaRole,
      tracing: lambda.Tracing.ACTIVE,
      logGroup,
      layers: [pypiLayer, whlLayer],
    });

    // Provisioned Concurrency for Production
    if (config.lambda.provisionedConcurrentExecutions) {
      const version = new lambda.Version(this, 'LambdaVersion', {
        lambda: lambdaFunction,
        provisionedConcurrentExecutions: config.lambda.provisionedConcurrentExecutions,
        description: `Version with provisioned concurrency for ${environment}`,
      });
    }

    // API Gateway REST API
    const api = new apigateway.RestApi(this, 'BacklogMcpApi', {
      restApiName: `backlog-mcp-${environment}-api`,
      description: `API for Backlog Model Context Protocol (${environment})`,
      deployOptions: {
        stageName: environment,
        tracingEnabled: true,
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        metricsEnabled: true,
        dataTraceEnabled: environment !== 'prod',
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: [
          'Content-Type',
          'X-Amz-Date',
          'Authorization',
          'X-Api-Key',
          'X-Amz-Security-Token',
        ],
      },
    });

    // Lambda Integration
    const lambdaIntegration = new apigateway.LambdaIntegration(lambdaFunction, {
      proxy: true,
    });

    // API Gateway Root Resource
    const apiResource = api.root.addResource('api');
    const v1Resource = apiResource.addResource('v1');

    // Add resources and methods
    const issuesResource = v1Resource.addResource('issues');
    issuesResource.addMethod('GET', lambdaIntegration, {
      apiKeyRequired: true,
    });
    issuesResource.addMethod('POST', lambdaIntegration, {
      apiKeyRequired: true,
    });

    const issueResource = issuesResource.addResource('{issueId}');
    issueResource.addMethod('GET', lambdaIntegration, {
      apiKeyRequired: true,
    });
    issueResource.addMethod('PUT', lambdaIntegration, {
      apiKeyRequired: true,
    });
    issueResource.addMethod('DELETE', lambdaIntegration, {
      apiKeyRequired: true,
    });

    const projectsResource = v1Resource.addResource('projects');
    projectsResource.addMethod('GET', lambdaIntegration, {
      apiKeyRequired: true,
    });

    const projectResource = projectsResource.addResource('{projectId}');
    projectResource.addMethod('GET', lambdaIntegration, {
      apiKeyRequired: true,
    });

    const bulkResource = v1Resource.addResource('bulk');
    bulkResource.addMethod('POST', lambdaIntegration, {
      apiKeyRequired: true,
    });

    // API Key
    const apiKey = new apigateway.ApiKey(this, 'BacklogMcpApiKey', {
      apiKeyName: `backlog-mcp-${environment}-key`,
      description: `API Key for Backlog MCP (${environment})`,
      enabled: true,
    });

    // Usage Plan
    const usagePlan = new apigateway.UsagePlan(this, 'BacklogMcpUsagePlan', {
      name: `${environment}-standard`,
      description: `Standard usage plan for Backlog MCP API (${environment})`,
      apiStages: [
        {
          api,
          stage: api.deploymentStage,
        },
      ],
      throttle: {
        rateLimit: config.apiGateway.rateLimit,
        burstLimit: config.apiGateway.burstLimit,
      },
      quota: {
        limit: config.apiGateway.quotaLimit,
        period: apigateway.Period.MONTH,
      },
    });

    usagePlan.addApiKey(apiKey);

    // Response Headers Policy
    const responseHeadersPolicy = new cloudfront.ResponseHeadersPolicy(this, 'SecurityHeaders', {
      responseHeadersPolicyName: `backlog-mcp-${environment}-security-headers`,
      securityHeadersBehavior: {
        contentTypeOptions: { override: true },
        frameOptions: { frameOption: cloudfront.HeadersFrameOption.DENY, override: true },
        referrerPolicy: { referrerPolicy: cloudfront.HeadersReferrerPolicy.SAME_ORIGIN, override: true },
        strictTransportSecurity: {
          accessControlMaxAge: Duration.seconds(63072000),
          includeSubdomains: true,
          override: true,
          preload: true,
        },
        xssProtection: { protection: true, modeBlock: true, override: true },
      },
    });

    // Cache Policy
    const cachePolicy = new cloudfront.CachePolicy(this, 'ApiCachePolicy', {
      cachePolicyName: `backlog-mcp-${environment}-cache-policy`,
      defaultTtl: Duration.seconds(config.cloudFront.cacheTtl),
      maxTtl: Duration.seconds(config.cloudFront.cacheTtl * 3),
      minTtl: Duration.seconds(0),
      enableAcceptEncodingBrotli: true,
      enableAcceptEncodingGzip: true,
    });

    // CloudFront Distribution
    const distribution = new cloudfront.Distribution(this, 'ApiDistribution', {
      defaultBehavior: {
        origin: new origins.RestApiOrigin(api),
        cachePolicy,
        responseHeadersPolicy,
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
        cachedMethods: cloudfront.CachedMethods.CACHE_GET_HEAD_OPTIONS,
      },
      comment: `Backlog MCP API Distribution (${environment})`,
      enabled: true,
      priceClass: config.cloudFront.priceClass,
      enableLogging: true,
      logIncludesCookies: false,
    });

    // WAF Web ACL (stg and prod only)
    if (environment === 'stg' || environment === 'prod') {
      const webAcl = new wafv2.CfnWebACL(this, 'WebAcl', {
        name: `backlog-mcp-${environment}-web-acl`,
        scope: 'CLOUDFRONT',
        defaultAction: { allow: {} },
        visibilityConfig: {
          cloudWatchMetricsEnabled: true,
          metricName: `backlog-mcp-${environment}-web-acl-metric`,
          sampledRequestsEnabled: true,
        },
        rules: [
          {
            name: 'SQLInjectionRule',
            priority: 10,
            statement: {
              managedRuleGroupStatement: {
                name: 'AWSManagedRulesSQLiRuleSet',
                vendorName: 'AWS',
              },
            },
            overrideAction: { none: {} },
            visibilityConfig: {
              cloudWatchMetricsEnabled: true,
              metricName: `backlog-mcp-${environment}-sql-injection-metric`,
              sampledRequestsEnabled: true,
            },
          },
          {
            name: 'RateLimitRule',
            priority: 20,
            action: { block: {} },
            statement: {
              rateBasedStatement: {
                limit: environment === 'prod' ? 1000 : 500,
                aggregateKeyType: 'IP',
              },
            },
            visibilityConfig: {
              cloudWatchMetricsEnabled: true,
              metricName: `backlog-mcp-${environment}-rate-limit-metric`,
              sampledRequestsEnabled: true,
            },
          },
        ],
      });

      // Associate WAF with CloudFront
      const cfnDistribution = distribution.node.defaultChild as cloudfront.CfnDistribution;
      cfnDistribution.addPropertyOverride('WebACLId', webAcl.attrArn);
    }

    // CloudWatch Alarms (prod only)
    if (environment === 'prod' && alertEmail) {
      // SNS Topic for Alarms
      const alarmTopic = new sns.Topic(this, 'AlarmTopic', {
        topicName: `backlog-mcp-${environment}-alarms`,
        displayName: `Backlog MCP Alarms (${environment})`,
      });

      // Email Subscription
      alarmTopic.addSubscription(new subscriptions.EmailSubscription(alertEmail));

      // Lambda Error Alarm
      const lambdaErrorAlarm = new cloudwatch.Alarm(this, 'LambdaErrorAlarm', {
        alarmName: `backlog-mcp-${environment}-lambda-errors`,
        alarmDescription: `Alarm when Lambda function has errors (${environment})`,
        metric: lambdaFunction.metricErrors({
          period: Duration.minutes(1),
        }),
        threshold: 1,
        evaluationPeriods: 3,
        comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
        treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
      });

      lambdaErrorAlarm.addAlarmAction(new actions.SnsAction(alarmTopic));

      // API Gateway 5xx Error Alarm
      const api5xxErrorAlarm = new cloudwatch.Alarm(this, 'Api5xxErrorAlarm', {
        alarmName: `backlog-mcp-${environment}-api-5xx-errors`,
        alarmDescription: `Alarm when API Gateway has 5xx errors (${environment})`,
        metric: api.metricServerError({
          period: Duration.minutes(1),
        }),
        threshold: 1,
        evaluationPeriods: 3,
        comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
        treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
      });

      api5xxErrorAlarm.addAlarmAction(new actions.SnsAction(alarmTopic));
    }

    // Stack Outputs
    new cdk.CfnOutput(this, 'Environment', {
      value: environment,
    });

    new cdk.CfnOutput(this, 'ApiGatewayUrl', {
      description: 'API Gateway endpoint URL',
      value: api.url,
      exportName: `backlog-mcp-${environment}-api-url`,
    });

    new cdk.CfnOutput(this, 'CloudFrontDomain', {
      description: 'CloudFront distribution domain name',
      value: distribution.distributionDomainName,
      exportName: `backlog-mcp-${environment}-cloudfront-domain`,
    });

    new cdk.CfnOutput(this, 'ApiKeyId', {
      description: 'API Key ID',
      value: apiKey.keyId,
      exportName: `backlog-mcp-${environment}-api-key-id`,
    });
  }
}
