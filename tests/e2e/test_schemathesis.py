import httpx # 追加
import schemathesis
import pytest
from fastapi.testclient import TestClient
from app.main import app  # FastAPIアプリケーションインスタンスをインポート
from hypothesis import settings

# モンキーパッチ: httpx.Requestにuriプロパティを追加
if not hasattr(httpx.Request, 'uri'):
    def get_uri(self_req: httpx.Request) -> httpx.URL:
        return str(self_req.url) # str() で囲む

    def set_uri(self_req: httpx.Request, value: str | httpx.URL) -> None:
        if isinstance(value, str):
            self_req.url = httpx.URL(value)
        elif isinstance(value, httpx.URL):
            self_req.url = value
        else:
            # Fallback or error, for now, convert to string then to URL
            self_req.url = httpx.URL(str(value))

    setattr(httpx.Request, 'uri', property(get_uri, set_uri))

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
    # ボディを持つ可能性のあるメソッドの場合のみjsonパラメータを設定
    if case.method.upper() not in ("GET", "DELETE", "HEAD", "OPTIONS") and case.body is not schemathesis.types.NotSet:
        request_kwargs["json"] = case.body
    if case.query is not schemathesis.types.NotSet:
        request_kwargs["params"] = case.query

    response = client.request(**request_kwargs)
    case.validate_response(response)