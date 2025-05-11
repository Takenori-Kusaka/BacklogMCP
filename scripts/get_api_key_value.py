import argparse
import boto3
import os

def get_api_key_value(api_key_id: str, region_name: str) -> str | None:
    """
    指定されたAPIキーIDに対応するAPIキーの値を取得します。

    Args:
        api_key_id: 取得するAPIキーのID。
        region_name: APIキーがデプロイされているAWSリージョン。

    Returns:
        APIキーの値。見つからない場合はNone。
    """
    try:
        client = boto3.client('apigateway', region_name=region_name)
        response = client.get_api_key(
            apiKey=api_key_id,
            includeValue=True
        )
        return response.get('value')
    except Exception as e:
        print(f"Error getting API key value: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get API Gateway API Key value.")
    parser.add_argument(
        "--api-key-id",
        required=True,
        help="API Key ID to retrieve the value for."
    )
    parser.add_argument(
        "--region",
        default=os.environ.get("AWS_REGION", "ap-northeast-1"), # 環境変数 AWS_REGION があればそれを使う
        help="AWS region where the API Key is deployed (default: ap-northeast-1)."
    )
    args = parser.parse_args()

    api_key_value = get_api_key_value(args.api_key_id, args.region)

    if api_key_value:
        print(api_key_value)
    else:
        print(f"Could not retrieve API key value for ID: {args.api_key_id}")