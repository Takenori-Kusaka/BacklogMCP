#!/bin/bash

# Node.jsのバージョンを確認
NODE_VERSION=$(node -v)
REQUIRED_VERSION="v14.15.0"

# バージョン比較関数
function version_lt() { 
    test "$(echo "$@" | tr " " "\n" | sort -rV | head -n 1)" != "$1"; 
}

# Node.jsのバージョンが必要なバージョンより低い場合は警告を表示
if version_lt "${NODE_VERSION}" "${REQUIRED_VERSION}"; then
    echo "警告: Node.jsのバージョンが古すぎます（${NODE_VERSION}）"
    echo "AWS CDKは Node.js ${REQUIRED_VERSION} 以上が必要です"
    echo "テストが失敗する可能性があります"
    echo ""
    echo "Node.jsをアップグレードするには以下のコマンドを実行してください："
    echo "  curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash - && sudo apt-get install -y nodejs"
    echo ""
    read -p "それでもテストを実行しますか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# ファイルをコピー
echo "ファイルをコピー中..."
mkdir -p lib
mkdir -p src/lib

# ファイルの存在を確認
echo "ファイルの存在を確認中..."
find . -name "backlog-mcp-stack.ts" -type f

# ファイルをコピー
if [ -f "lib/backlog-mcp-stack.ts" ]; then
  echo "lib/backlog-mcp-stack.ts が存在します。src/lib にコピーします。"
  cp -f lib/backlog-mcp-stack.ts src/lib/
fi

# ファイルを直接作成
echo "ファイルを直接作成します..."
cat > lib/backlog-mcp-stack.ts << 'EOL'
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as wafv2 from 'aws-cdk-lib/aws-wafv2';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import * as cloudwatch_actions from 'aws-cdk-lib/aws-cloudwatch-actions';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as iam from 'aws-cdk-lib/aws-iam';

export interface BacklogMcpStackProps extends cdk.StackProps {
  environment: 'dev' | 'stg' | 'prod';
  alertEmail?: string;
}

export class BacklogMcpStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: BacklogMcpStackProps) {
    super(scope, id, props);

    const { environment, alertEmail } = props;

    // 環境ごとの設定
    const config = {
      dev: {
        lambdaMemory: 512,
        logLevel: 'debug',
        apiRateLimit: 50,
        apiBurstLimit: 25,
        apiQuota: 5000,
        cloudfrontPriceClass: cloudfront.PriceClass.PRICE_CLASS_100,
        enableWaf: false,
        enableAlarms: false,
      },
      stg: {
        lambdaMemory: 1024,
        logLevel: 'debug',
        apiRateLimit: 100,
        apiBurstLimit: 50,
        apiQuota: 10000,
        cloudfrontPriceClass: cloudfront.PriceClass.PRICE_CLASS_100,
        enableWaf: true,
        enableAlarms: false,
      },
      prod: {
        lambdaMemory: 2048,
        logLevel: 'info',
        apiRateLimit: 500,
        apiBurstLimit: 100,
        apiQuota: 1000000,
        cloudfrontPriceClass: cloudfront.PriceClass.PRICE_CLASS_ALL,
        enableWaf: true,
        enableAlarms: true,
      },
    };

    const envConfig = config[environment];

    // Lambda関数の作成
    const lambdaFunction = new lambda.Function(this, 'BacklogMcpFunction', {
      functionName: `backlog-mcp-${environment}-function`,
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'index.handler',
      code: lambda.Code.fromInline('exports.handler = async () => { return { statusCode: 200, body: JSON.stringify({ message: "Hello from Lambda!" }) }; }'),
      memorySize: envConfig.lambdaMemory,
      timeout: cdk.Duration.seconds(30),
      environment: {
        TZ: 'Asia/Tokyo',
        NODE_ENV: environment,
        LOG_LEVEL: envConfig.logLevel,
      },
    });

    // CloudWatch Logsの設定
    const logGroup = new logs.LogGroup(this, 'BacklogMcpLogs', {
      logGroupName: `/aws/lambda/backlog-mcp-${environment}-function`,
      retention: logs.RetentionDays.TWO_WEEKS,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // API Gatewayの作成
    const api = new apigateway.RestApi(this, 'BacklogMcpApi', {
      restApiName: `backlog-mcp-${environment}-api`,
      description: 'Backlog MCP API',
      deployOptions: {
        stageName: 'v1',
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
      },
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: ['Content-Type', 'X-Api-Key', 'Authorization'],
      },
    });

    // APIキーとUsage Planの作成
    const apiKey = api.addApiKey('BacklogMcpApiKey', {
      apiKeyName: `backlog-mcp-${environment}-api-key`,
      description: 'API Key for Backlog MCP API',
    });

    const usagePlan = api.addUsagePlan('BacklogMcpUsagePlan', {
      name: `backlog-mcp-${environment}-usage-plan`,
      description: 'Usage Plan for Backlog MCP API',
      apiStages: [
        {
          api,
          stage: api.deploymentStage,
        },
      ],
      throttle: {
        rateLimit: envConfig.apiRateLimit,
        burstLimit: envConfig.apiBurstLimit,
      },
      quota: {
        limit: envConfig.apiQuota,
        period: apigateway.Period.MONTH,
      },
    });

    usagePlan.addApiKey(apiKey);

    // APIリソースの作成
    const apiResource = api.root.addResource('api');
    const v1Resource = apiResource.addResource('v1');
    
    // issuesリソースの作成
    const issuesResource = v1Resource.addResource('issues');
    issuesResource.addMethod('GET', new apigateway.LambdaIntegration(lambdaFunction), {
      apiKeyRequired: true,
    });
    issuesResource.addMethod('POST', new apigateway.LambdaIntegration(lambdaFunction), {
      apiKeyRequired: true,
    });

    // projectsリソースの作成
    const projectsResource = v1Resource.addResource('projects');
    projectsResource.addMethod('GET', new apigateway.LambdaIntegration(lambdaFunction), {
      apiKeyRequired: true,
    });

    // bulkリソースの作成
    const bulkResource = v1Resource.addResource('bulk');
    bulkResource.addMethod('POST', new apigateway.LambdaIntegration(lambdaFunction), {
      apiKeyRequired: true,
    });

    // CloudFrontの設定
    const responseHeadersPolicy = new cloudfront.ResponseHeadersPolicy(this, 'SecurityHeadersPolicy', {
      responseHeadersPolicyName: `backlog-mcp-${environment}-security-headers`,
      securityHeadersBehavior: {
        contentTypeOptions: { override: true },
        frameOptions: {
          frameOption: cloudfront.HeadersFrameOption.DENY,
          override: true,
        },
        referrerPolicy: {
          referrerPolicy: cloudfront.HeadersReferrerPolicy.SAME_ORIGIN,
          override: true,
        },
        strictTransportSecurity: {
          accessControlMaxAge: cdk.Duration.seconds(63072000),
          includeSubdomains: true,
          preload: true,
          override: true,
        },
        xssProtection: {
          protection: true,
          modeBlock: true,
          override: true,
        },
      },
    });

    const cachePolicy = new cloudfront.CachePolicy(this, 'CachePolicy', {
      cachePolicyName: `backlog-mcp-${environment}-cache-policy`,
      defaultTtl: cdk.Duration.seconds(0),
      minTtl: cdk.Duration.seconds(0),
      maxTtl: cdk.Duration.seconds(1),
      enableAcceptEncodingGzip: true,
      enableAcceptEncodingBrotli: true,
    });

    // CloudFrontディストリビューションの作成
    const distribution = new cloudfront.Distribution(this, 'BacklogMcpDistribution', {
      defaultBehavior: {
        origin: new origins.RestApiOrigin(api),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
        cachedMethods: cloudfront.CachedMethods.CACHE_GET_HEAD_OPTIONS,
        cachePolicy,
        responseHeadersPolicy,
      },
      priceClass: envConfig.cloudfrontPriceClass,
    });

    // WAFの設定（stgとprod環境のみ）
    if (envConfig.enableWaf) {
      const webAcl = new wafv2.CfnWebACL(this, 'BacklogMcpWebAcl', {
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
            name: 'RateLimitRule',
            priority: 1,
            action: { block: {} },
            statement: {
              rateBasedStatement: {
                limit: 1000,
                aggregateKeyType: 'IP',
              },
            },
            visibilityConfig: {
              cloudWatchMetricsEnabled: true,
              metricName: `backlog-mcp-${environment}-rate-limit-rule-metric`,
              sampledRequestsEnabled: true,
            },
          },
          {
            name: 'AWSManagedRulesCommonRuleSet',
            priority: 2,
            overrideAction: { none: {} },
            statement: {
              managedRuleGroupStatement: {
                vendorName: 'AWS',
                name: 'AWSManagedRulesCommonRuleSet',
              },
            },
            visibilityConfig: {
              cloudWatchMetricsEnabled: true,
              metricName: `backlog-mcp-${environment}-aws-common-rule-metric`,
              sampledRequestsEnabled: true,
            },
          },
        ],
      });

      // CloudFrontとWAFの関連付け
      const cfnDistribution = distribution.node.defaultChild as cloudfront.CfnDistribution;
      cfnDistribution.addPropertyOverride('WebACLId', webAcl.attrArn);
    }

    // CloudWatch Alarmsの設定（prod環境のみ）
    if (envConfig.enableAlarms && alertEmail) {
      // SNS Topicの作成
      const alarmTopic = new sns.Topic(this, 'BacklogMcpAlarmTopic', {
        topicName: `backlog-mcp-${environment}-alarms`,
      });

      // メール通知の設定
      alarmTopic.addSubscription(new subscriptions.EmailSubscription(alertEmail));

      // Lambda関数のエラーアラーム
      new cloudwatch.Alarm(this, 'LambdaErrorsAlarm', {
        alarmName: `backlog-mcp-${environment}-lambda-errors`,
        metric: lambdaFunction.metricErrors({
          period: cdk.Duration.minutes(5),
        }),
        threshold: 5,
        evaluationPeriods: 1,
        comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        alarmDescription: 'Alarm when Lambda function has too many errors',
        treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
      }).addAlarmAction(new cloudwatch_actions.SnsAction(alarmTopic));

      // API Gateway 5xxエラーアラーム
      new cloudwatch.Alarm(this, 'ApiGateway5xxErrorsAlarm', {
        alarmName: `backlog-mcp-${environment}-api-5xx-errors`,
        metric: api.metricServerError({
          period: cdk.Duration.minutes(5),
        }),
        threshold: 5,
        evaluationPeriods: 1,
        comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
        alarmDescription: 'Alarm when API Gateway has too many 5xx errors',
        treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
      }).addAlarmAction(new cloudwatch_actions.SnsAction(alarmTopic));
    }

    // 出力
    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: api.url,
      description: 'API Gateway Endpoint',
    });

    new cdk.CfnOutput(this, 'CloudFrontDomain', {
      value: distribution.distributionDomainName,
      description: 'CloudFront Domain Name',
    });

    new cdk.CfnOutput(this, 'ApiKeyId', {
      value: apiKey.keyId,
      description: 'API Key ID',
    });
  }
}
EOL

# src/libにもコピー
cp -f lib/backlog-mcp-stack.ts src/lib/

# テストを実行
echo "テストを実行中..."
npm test -- --no-cache --no-watchman
