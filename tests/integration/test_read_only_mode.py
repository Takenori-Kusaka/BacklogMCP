import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.core.config import settings
from app.infrastructure.backlog.backlog_client_wrapper import BacklogClientWrapper # Wrapperをインポート

client = TestClient(app)


@pytest.mark.asyncio
async def test_read_only_mode_disabled_allows_write_api(monkeypatch): # APIレベルのテストであることを明示
    """読み取り専用モードが無効な場合、書き込み操作が許可されることをテストします。"""
    monkeypatch.setattr(settings, "READ_ONLY_MODE", False)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 課題作成APIエンドポイントを使用
        response = await ac.post("/api/issues/", json={"summary": "Test Issue from API"})
    assert response.status_code != 403 # 403 Forbiddenではないことを確認 (実際の成功/失敗はAPI実装による)


@pytest.mark.asyncio
async def test_read_only_mode_enabled_blocks_write_api(monkeypatch): # APIレベルのテストであることを明示
    """読み取り専用モードが有効な場合、書き込み操作がブロックされることをテストします。"""
    monkeypatch.setattr(settings, "READ_ONLY_MODE", True)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 課題作成APIエンドポイントを使用
        response = await ac.post("/api/issues/", json={"summary": "Test Issue from API"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Application is in read-only mode. Write operations are disabled."}

@pytest.mark.asyncio
async def test_read_only_mode_disabled_allows_get_api(monkeypatch): # APIレベルのテストであることを明示
    """読み取り専用モードが無効な場合、読み取り操作が許可されることをテストします。"""
    monkeypatch.setattr(settings, "READ_ONLY_MODE", False)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/issues/") # 課題取得APIエンドポイントを使用
    assert response.status_code != 403 # 403以外であることを確認

@pytest.mark.asyncio
async def test_read_only_mode_enabled_allows_get_api(monkeypatch): # APIレベルのテストであることを明示
    """読み取り専用モードが有効な場合でも、読み取り操作が許可されることをテストします。"""
    monkeypatch.setattr(settings, "READ_ONLY_MODE", True)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/issues/") # 課題取得APIエンドポイントを使用
    assert response.status_code != 403 # 403以外であることを確認

# BacklogClientWrapperレベルのテスト
def test_backlog_client_read_only_mode_create_issue():
    """BacklogClientWrapperが読み取り専用モードの場合、create_issueがPermissionErrorを送出することを確認します。"""
    client_wrapper = BacklogClientWrapper(api_key="dummy_key", space="dummy_space", read_only_mode=True)
    with pytest.raises(PermissionError, match="Cannot create issue in read-only mode."):
        client_wrapper.create_issue(project_id=1, summary="Test")

def test_backlog_client_read_only_mode_update_issue():
    """BacklogClientWrapperが読み取り専用モードの場合、update_issueがPermissionErrorを送出することを確認します。"""
    client_wrapper = BacklogClientWrapper(api_key="dummy_key", space="dummy_space", read_only_mode=True)
    with pytest.raises(PermissionError, match="Cannot update issue in read-only mode."):
        client_wrapper.update_issue(issue_id_or_key="TEST-1", summary="Test Update")

def test_backlog_client_read_only_mode_delete_issue():
    """BacklogClientWrapperが読み取り専用モードの場合、delete_issueがPermissionErrorを送出することを確認します。"""
    client_wrapper = BacklogClientWrapper(api_key="dummy_key", space="dummy_space", read_only_mode=True)
    with pytest.raises(PermissionError, match="Cannot delete issue in read-only mode."):
        client_wrapper.delete_issue(issue_id_or_key="TEST-1")

def test_backlog_client_read_only_mode_add_comment():
    """BacklogClientWrapperが読み取り専用モードの場合、add_commentがPermissionErrorを送出することを確認します。"""
    client_wrapper = BacklogClientWrapper(api_key="dummy_key", space="dummy_space", read_only_mode=True)
    with pytest.raises(PermissionError, match="Cannot add comment in read-only mode."):
        client_wrapper.add_comment(issue_id_or_key="TEST-1", content="Test comment")

def test_backlog_client_read_write_mode_allows_write_operations():
    """BacklogClientWrapperが読み書きモードの場合、書き込み操作がエラーを送出しないことを確認します（実際のAPI呼び出しはモックする）。"""
    client_wrapper = BacklogClientWrapper(api_key="dummy_key", space="dummy_space", read_only_mode=False)
    
    # 実際のAPI呼び出しをモックして、PermissionErrorが発生しないことだけを確認
    with monkeypatch.context() as m:
        m.setattr(client_wrapper.issue_api, "add_issue", lambda **kwargs: {"id": 1}) # モックされたレスポンス
        try:
            client_wrapper.create_issue(project_id=1, summary="Test")
        except PermissionError:
            pytest.fail("PermissionError was raised in read-write mode for create_issue")

    with monkeypatch.context() as m:
        # update_issueはget_issueを内部で呼ぶため、それもモックする
        m.setattr(client_wrapper.issue_api, "get_issue", lambda issue_id_or_key: {"id": 1, "projectId": 1})
        m.setattr(client_wrapper.issue_api, "update_issue", lambda **kwargs: {"id": 1})
        try:
            client_wrapper.update_issue(issue_id_or_key="TEST-1", summary="Test Update")
        except PermissionError:
            pytest.fail("PermissionError was raised in read-write mode for update_issue")

    with monkeypatch.context() as m:
        m.setattr(client_wrapper.issue_api, "delete_issue", lambda issue_id_or_key: type('obj', (object,), {'status_code': 200, 'ok': True})())
        try:
            client_wrapper.delete_issue(issue_id_or_key="TEST-1")
        except PermissionError:
            pytest.fail("PermissionError was raised in read-write mode for delete_issue")

    with monkeypatch.context() as m:
        m.setattr(client_wrapper.issue_comment_api, "add_comment", lambda **kwargs: {"id": 1})
        try:
            client_wrapper.add_comment(issue_id_or_key="TEST-1", content="Test comment")
        except PermissionError:
            pytest.fail("PermissionError was raised in read-write mode for add_comment")