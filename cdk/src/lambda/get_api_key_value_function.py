import json
import os
import boto3

def lambda_handler(event, context):
    """
    API GatewayのAPIキーの値を取得するLambda関数。
    環境変数 API_KEY_ID からAPIキーIDを読み込み、
    実行リージョンを自動的に使用する。
    """
    api_key_id = os.environ.get('API_KEY_ID')
    region_name = os.environ.get('AWS_REGION')

    if not api_key_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Environment variable API_KEY_ID is not set'})
        }
    if not region_name:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'AWS_REGION environment variable is not set (should be set by Lambda runtime)'})
        }

    try:
        client = boto3.client('apigateway', region_name=region_name)
        response = client.get_api_key(
            apiKey=api_key_id,
            includeValue=True
        )
        api_key_value = response.get('value')

        if api_key_value:
            return {
                'statusCode': 200,
                'body': json.dumps({'api_key_id': api_key_id, 'api_key_value': api_key_value})
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'API Key not found for ID: {api_key_id}'})
            }
    except Exception as e:
        print(f"Error getting API key value: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }