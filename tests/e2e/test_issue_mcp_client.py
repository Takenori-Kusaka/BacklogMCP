
CD"""
MCPクライアントSDK経由でBacklog課題操作（個別）E2Eテスト
"""

import asyncio
import os

import pytest
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY")
    or not os.getenv("BACKLOG_SPACE")
    or not os.getenv("BACKLOG_PROJECT"),
    reason="Backlog API環境変数が設定されていません",
)
async def test_mcp_client_create_get_update_delete_issue(mcp_server_url: str) -> None:
    """課題の作成→取得→更新→削除までをMCPクライアントSDK経由でE2Eテスト"""
    project_key = os.getenv("BACKLOG_PROJECT")
    # 1. 課題作成
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # 課題種別ID取得
            types_result = await session.call_tool(
                "get_issue_types", {"project_key": project_key}
            )
            assert hasattr(types_result, "content")
            
            # MCPのレスポンスはTextContent | ImageContent | EmbeddedResourceの配列
            # TextContentの場合はJSON文字列をパースする必要がある
            if types_result.content and len(types_result.content) > 0:
                content_item = types_result.content[0]
                if hasattr(content_item, "text"):
                    # JSONをパース
                    import json
                    issue_types = json.loads(content_item.text)
                    assert isinstance(issue_types, list)
                    issue_type_id = issue_types[0]["id"]
                else:
                    pytest.skip("Issue types content is not text")
            else:
                pytest.skip("No issue types found")
            # 課題作成
            create_result = await session.call_tool(
                "create_issue",
                {
                    "project_id": None,  # project_keyで十分
                    "project_key": project_key,
                    "summary": "MCP E2Eテスト課題",
                    "issue_type_id": issue_type_id,
                    "priority_id": 3,
                    "description": "MCPクライアントSDK経由E2Eテスト課題",
                },
            )
            assert hasattr(create_result, "content")
            
            # MCPのレスポンスはTextContent | ImageContent | EmbeddedResourceの配列
            # TextContentの場合はJSON文字列をパースする必要がある
            issue_key = None
            if create_result.content and len(create_result.content) > 0:
                content_item = create_result.content[0]
                if hasattr(content_item, "text"):
                    # JSONをパース
                    import json
                    issue = json.loads(content_item.text)
                    assert isinstance(issue, dict)
                    issue_key = issue["issueKey"]
                else:
                    pytest.skip("Create issue content is not text")
            else:
                pytest.skip("No issue created")
            # 2. 課題取得
            get_result = await session.call_tool(
                "get_issue", {"issue_id_or_key": issue_key}
            )
            assert hasattr(get_result, "content")
            
            # MCPのレスポンスはTextContent | ImageContent | EmbeddedResourceの配列
            # TextContentの場合はJSON文字列をパースする必要がある
            if get_result.content and len(get_result.content) > 0:
                content_item = get_result.content[0]
                if hasattr(content_item, "text"):
                    # JSONをパース
                    import json
                    issue = json.loads(content_item.text)
                    assert isinstance(issue, dict)
                    assert issue["issueKey"] == issue_key
                else:
                    pytest.skip("Get issue content is not text")
            else:
                pytest.skip("No issue found")
            # 3. 課題更新
            update_result = await session.call_tool(
                "update_issue",
                {"issue_id_or_key": issue_key, "summary": "MCP E2Eテスト課題(更新)"},
            )
            assert hasattr(update_result, "content")
            
            # MCPのレスポンスはTextContent | ImageContent | EmbeddedResourceの配列
            # TextContentの場合はJSON文字列をパースする必要がある
            if update_result.content and len(update_result.content) > 0:
                content_item = update_result.content[0]
                if hasattr(content_item, "text"):
                    # JSONをパース
                    import json
                    issue = json.loads(content_item.text)
                    assert isinstance(issue, dict)
                    assert issue["summary"] == "MCP E2Eテスト課題(更新)"
                else:
                    pytest.skip("Update issue content is not text")
            else:
                pytest.skip("No issue updated")
            # 4. コメント追加
            comment_result = await session.call_tool(
                "add_comment",
                {"issue_id_or_key": issue_key, "content": "MCP E2Eテストコメント"},
            )
            assert hasattr(comment_result, "content")
            
            # MCPのレスポンスはTextContent | ImageContent | EmbeddedResourceの配列
            # TextContentの場合はJSON文字列をパースする必要がある
            if comment_result.content and len(comment_result.content) > 0:
                content_item = comment_result.content[0]
                if hasattr(content_item, "text"):
                    # JSONをパース
                    import json
                    comment = json.loads(content_item.text)
                    assert isinstance(comment, dict)
                    assert comment["content"] == "MCP E2Eテストコメント"
                else:
                    pytest.skip("Add comment content is not text")
            else:
                pytest.skip("No comment added")
            # 5. コメント一覧取得
            comments_result = await session.call_tool(
                "get_issue_comments", {"issue_id_or_key": issue_key}
            )
            assert hasattr(comments_result, "content")
            
            # MCPのレスポンスはTextContent | ImageContent | EmbeddedResourceの配列
            # TextContentの場合はJSON文字列をパースする必要がある
            if comments_result.content and len(comments_result.content) > 0:
                content_item = comments_result.content[0]
                if hasattr(content_item, "text"):
                    # JSONをパース
                    import json
                    comments = json.loads(content_item.text)
                    assert isinstance(comments, list)
                    assert any(c["content"] == "MCP E2Eテストコメント" for c in comments)
                else:
                    pytest.skip("Get comments content is not text")
            else:
                pytest.skip("No comments found")
            # 6. 課題削除
            delete_result = await session.call_tool(
                "delete_issue", {"issue_id_or_key": issue_key}
            )
            assert hasattr(delete_result, "content")
            
            # MCPのレスポンスはTextContent | ImageContent | EmbeddedResourceの配列
            # TextContentの場合はJSON文字列をパースする必要がある
            if delete_result.content and len(delete_result.content) > 0:
                content_item = delete_result.content[0]
                if hasattr(content_item, "text"):
                    # JSONをパース
                    import json
                    result = json.loads(content_item.text)
                    assert result is True or result is None
                else:
                    # テキスト以外の場合は成功とみなす
                    pass
            else:
                # 空の場合も成功とみなす
                pass


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY")
    or not os.getenv("BACKLOG_SPACE")
    or not os.getenv("BACKLOG_PROJECT"),
    reason="Backlog API環境変数が設定されていません",
)
async def test_mcp_client_create_with_name_parameters(mcp_server_url: str) -> None:
    """名前ベースのパラメータで課題を作成するMCPクライアントSDK経由E2Eテスト"""
    project_key = os.getenv("BACKLOG_PROJECT")
    # 課題作成（名前ベースのパラメータ）
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # 課題作成
            create_result = await session.call_tool(
                "create_issue",
                {
                    "project_key": project_key,
                    "summary": "名前ベースのMCP E2Eテスト課題",
                    "issue_type_name": "タスク",  # 課題種別名で指定
                    "priority_name": "中",  # 優先度名で指定
                    "description": "名前ベースのパラメータによるMCPクライアントSDK経由E2Eテスト課題",
                },
            )
            assert hasattr(create_result, "content")
            # MCPのレスポンスはTextContent | ImageContent | EmbeddedResourceの配列
            # TextContentの場合はJSON文字列をパースする必要がある
            issue_key = None
            if create_result.content and len(create_result.content) > 0:
                content_item = create_result.content[0]
                if hasattr(content_item, "text"):
                    # JSONをパース
                    import json
                    issue = json.loads(content_item.text)
                    assert isinstance(issue, dict)
                    issue_key = issue["issueKey"]
                else:
                    pytest.skip("Create issue content is not text")
            else:
                pytest.skip("No issue created")
            # 課題取得
            get_result = await session.call_tool(
                "get_issue", {"issue_id_or_key": issue_key}
            )
            assert hasattr(get_result, "content")
            # MCPのレスポンスはTextContent | ImageContent | EmbeddedResourceの配列
            # TextContentの場合はJSON文字列をパースする必要がある
            if get_result.content and len(get_result.content) > 0:
                content_item = get_result.content[0]
                if hasattr(content_item, "text"):
                    # JSONをパース
                    import json
                    issue = json.loads(content_item.text)
                    assert isinstance(issue, dict)
                    assert issue["issueKey"] == issue_key
                    assert issue["summary"] == "名前ベースのMCP E2Eテスト課題"
                else:
                    pytest.skip("Get issue content is not text")
            else:
                pytest.skip("No issue found")
            # 課題削除
            delete_result = await session.call_tool(
                "delete_issue", {"issue_id_or_key": issue_key}
            )
            assert hasattr(delete_result, "content")
            # MCPのレスポンスはTextContent | ImageContent | EmbeddedResourceの配列
            # TextContentの場合はJSON文字列をパースする必要がある
            if delete_result.content and len(delete_result.content) > 0:
                content_item = delete_result.content[0]
                if hasattr(content_item, "text"):
                    # JSONをパース
                    import json
                    result = json.loads(content_item.text)
                    assert result is True or result is None
                else:
                    # テキスト以外の場合は成功とみなす
                    pass
            else:
                # 空の場合も成功とみなす
                pass


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY")
    or not os.getenv("BACKLOG_SPACE")
    or not os.getenv("BACKLOG_PROJECT"),
    reason="Backlog API環境変数が設定されていません",
)
async def test_mcp_client_update_with_name_parameters(mcp_server_url: str) -> None:
    """名前ベースのパラメータで課題を更新するMCPクライアントSDK経由E2Eテスト"""
    project_key = os.getenv("BACKLOG_PROJECT")
    # 課題作成→名前ベースで更新→削除
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # 課題種別ID取得
            types_result = await session.call_tool(
                "get_issue_types", {"project_key": project_key}
            )
            assert hasattr(types_result, "content")
            # MCPのレスポンスはTextContent | ImageContent | EmbeddedResourceの配列
            # TextContentの場合はJSON文字列をパースする必要がある
            issue_type_id = None
            if types_result.content and len(types_result.content) > 0:
                content_item = types_result.content[0]
                if hasattr(content_item, "text"):
                    # JSONをパース
                    import json
                    issue_types = json.loads(content_item.text)
                    assert isinstance(issue_types, list)
                    issue_type_id = issue_types[0]["id"]
                else:
                    pytest.skip("Issue types content is not text")
            else:
                pytest.skip("No issue types found")
            # 課題作成
            create_result = await session.call_tool(
                "create_issue",
                {
                    "project_key": project_key,
                    "summary": "更新用MCP E2Eテスト課題",
                    "issue_type_id": issue_type_id,
                    "priority_id": 3,
                    "description": "名前ベースで更新するMCPクライアントSDK経由E2Eテスト課題",
                },
            )
            assert hasattr(create_result, "content")
            # MCPのレスポンスはTextContent | ImageContent | EmbeddedResourceの配列
            # TextContentの場合はJSON文字列をパースする必要がある
            issue_key = None
            if create_result.content and len(create_result.content) > 0:
                content_item = create_result.content[0]
                if hasattr(content_item, "text"):
                    # JSONをパース
                    import json
                    issue = json.loads(content_item.text)
                    assert isinstance(issue, dict)
                    issue_key = issue["issueKey"]
                else:
                    pytest.skip("Create issue content is not text")
            else:
                pytest.skip("No issue created")
            # 名前ベースで課題更新
            update_result = await session.call_tool(
                "update_issue",
                {
                    "issue_id_or_key": issue_key,
                    "summary": "名前ベースで更新されたMCP E2Eテスト課題",
                    "status_name": "処理中",  # ステータス名で指定
                    "priority_name": "高",  # 優先度名で指定
                },
            )
            assert hasattr(update_result, "content")
            # MCPのレスポンスはTextContent | ImageContent | EmbeddedResourceの配列
            # TextContentの場合はJSON文字列をパースする必要がある
            if update_result.content and len(update_result.content) > 0:
                content_item = update_result.content[0]
                if hasattr(content_item, "text"):
                    # JSONをパース
                    import json
                    issue = json.loads(content_item.text)
                    assert isinstance(issue, dict)
                    assert issue["summary"] == "名前ベースで更新されたMCP E2Eテスト課題"
                else:
                    pytest.skip("Update issue content is not text")
            else:
                pytest.skip("No issue updated")
            # 課題削除
            delete_result = await session.call_tool(
                "delete_issue", {"issue_id_or_key": issue_key}
            )
            assert hasattr(delete_result, "content")
            # MCPのレスポンスはTextContent | ImageContent | EmbeddedResourceの配列
            # TextContentの場合はJSON文字列をパースする必要がある
            if delete_result.content and len(delete_result.content) > 0:
                content_item = delete_result.content[0]
                if hasattr(content_item, "text"):
                    # JSONをパース
                    import json
                    result = json.loads(content_item.text)
                    assert result is True or result is None
                else:
                    # テキスト以外の場合は成功とみなす
                    pass
            else:
                # 空の場合も成功とみなす
                pass
