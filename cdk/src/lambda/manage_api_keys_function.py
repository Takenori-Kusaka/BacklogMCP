import json
import os
import boto3
import uuid

def lambda_handler(event, context):
    """
    API GatewayのAPIキーと使用量プランを管理するLambda関数。
    現在は 'create' アクションのみをサポート。
    """
    action = event.get('action')
    region_name = os.environ.get('AWS_REGION')
    api_gateway_stage_arn = os.environ.get('API_GATEWAY_STAGE_ARN') # 例: arn:aws:apigateway:us-east-1::/restapis/xxxx/stages/dev

    if not region_name:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'AWS_REGION environment variable is not set'})
        }
    if not api_gateway_stage_arn:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'API_GATEWAY_STAGE_ARN environment variable is not set'})
        }

    client = boto3.client('apigateway', region_name=region_name)

    if action == 'create':
        key_name = event.get('keyName')
        description = event.get('description', f"API Key for {key_name}")
        # スロットリングとクォータのデフォルト値と型変換
        try:
            throttle_rate_limit = int(event.get('throttleRateLimit', 10))
            throttle_burst_limit = int(event.get('throttleBurstLimit', 5))
            quota_limit = int(event.get('quotaLimit', 10000))
            quota_period = event.get('quotaPeriod', 'MONTH').upper()
            if quota_period not in ['DAY', 'WEEK', 'MONTH']:
                raise ValueError("Invalid quotaPeriod. Must be DAY, WEEK, or MONTH.")
        except ValueError as e:
            return {'statusCode': 400, 'body': json.dumps({'error': f"Invalid throttle/quota parameter: {str(e)}"}) }


        if not key_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'keyName is required for create action'})
            }

        try:
            # 1. APIキーを作成
            api_key_response = client.create_api_key(
                name=key_name,
                description=description,
                enabled=True,
                generateDistinctId=True # 推奨
            )
            api_key_id = api_key_response['id']
            api_key_value = api_key_response['value'] # この値を発行者に返す

            # 2. 使用量プランを作成
            usage_plan_name = f"UsagePlan-{key_name.replace(' ', '-')}-{str(uuid.uuid4())[:8]}" # 一意なプラン名
            # API GatewayのステージARNからAPI IDとステージ名を取得
            # arn:aws:apigateway:{region}::/restapis/{api_id}/stages/{stage_name}
            parts = api_gateway_stage_arn.split(':')
            api_id_part = parts[5].split('/')
            api_id = api_id_part[2]
            stage_name = api_id_part[4]


            usage_plan_response = client.create_usage_plan(
                name=usage_plan_name,
                description=f"Usage plan for API Key {key_name}",
                apiStages=[
                    {
                        'apiId': api_id,
                        'stage': stage_name,
                        # スロットリング設定はステージごとにも設定可能だが、プラン全体で設定
                        # 'throttle': {
                        #     'resource_path': { # 特定リソースパスごとのスロットリング
                        #         'rateLimit': throttle_rate_limit,
                        #         'burstLimit': throttle_burst_limit
                        #     }
                        # }
                    }
                ],
                throttle={
                    'rateLimit': throttle_rate_limit,
                    'burstLimit': throttle_burst_limit
                },
                quota={
                    'limit': quota_limit,
                    'offset': 0, # 通常は0
                    'period': quota_period
                }
            )
            usage_plan_id = usage_plan_response['id']

            # 3. APIキーを使用量プランに関連付け
            client.create_usage_plan_key(
                usagePlanId=usage_plan_id,
                keyId=api_key_id,
                keyType='API_KEY' # 明示的に指定
            )

            return {
                'statusCode': 201,
                'body': json.dumps({
                    'message': 'API Key and Usage Plan created successfully',
                    'apiKeyId': api_key_id,
                    'apiKeyValue': api_key_value, # 注意: この値は安全に扱う必要があります
                    'usagePlanId': usage_plan_id,
                    'keyName': key_name,
                    'throttleRateLimit': throttle_rate_limit,
                    'throttleBurstLimit': throttle_burst_limit,
                    'quotaLimit': quota_limit,
                    'quotaPeriod': quota_period
                })
            }

        except Exception as e:
            # エラー発生時は作成されたリソースをクリーンアップするロジックも考慮が必要だが、ここでは省略
            print(f"Error creating API Key/Usage Plan: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f"Failed to create API Key/Usage Plan: {str(e)}"})
            }
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f"Action '{action}' is not supported. Only 'create' is currently supported."})
        }