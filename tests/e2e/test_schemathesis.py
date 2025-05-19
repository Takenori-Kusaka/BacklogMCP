import schemathesis
import pytest
from fastapi.testclient import TestClient
from app.main import app  # FastAPIアプリケーションインスタンスをインポート
from hypothesis import settings # settingsをインポート

# OpenAPIスキーマをローカルファイルからロード
# FastAPIアプリケーションが実行中である必要はありません
schema = schemathesis.from_path("docs/openapi.yaml")

# TestClientを使用してアプリケーションをテスト
client = TestClient(app)

@settings(deadline=None) # タイムアウトを無効化
@schema.parametrize()
def test_api(case):
    # TestClientを使用してリクエストを送信し、検証する
    request_kwargs = {
        "method": case.method,
        "url": case.formatted_path,
        "headers": case.headers,
    }
    if case.body is not schemathesis.types.NotSet: # NotSetでない場合のみjsonパラメータを追加
        request_kwargs["json"] = case.body
    if case.query is not schemathesis.types.NotSet: # NotSetでない場合のみparamsパラメータを追加
        request_kwargs["params"] = case.query

    response = client.request(**request_kwargs)
    case.validate_response(response)