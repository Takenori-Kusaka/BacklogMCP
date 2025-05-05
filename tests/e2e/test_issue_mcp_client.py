"""
MCPクライアントSDK経由でBacklog課題操作（個別）E2Eテスト
"""
import os
import asyncio
import pytest
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE") or not os.getenv("BACKLOG_PROJECT"),
    reason="Backlog API環境変数が設定されていません"
)
async def test_mcp_client_create_get_update_delete_issue(mcp_server_url):
    """課題の作成→取得→更新→削除までをMCPクライアントSDK経由でE2Eテスト"""
    project_key = os.getenv("BACKLOG_PROJECT")
    # 1. 課題作成
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # 課題種別ID取得
            types_result = await session.call_tool("get_issue_types", {"project_key": project_key})
            assert hasattr(types_result, "content")
            issue_type_id = types_result.content[0]["id"]
            # 課題作成
            create_result = await session.call_tool(
                "create_issue",
                {
                    "project_id": None,  # project_keyで十分
                    "project_key": project_key,
                    "summary": "MCP E2Eテスト課題",
                    "issue_type_id": issue_type_id,
                    "priority_id": 3,
                    "description": "MCPクライアントSDK経由E2Eテスト課題"
                }
            )
            assert hasattr(create_result, "content")
            issue_key = create_result.content["issueKey"]
            # 2. 課題取得
            get_result = await session.call_tool("get_issue", {"issue_id_or_key": issue_key})
            assert hasattr(get_result, "content")
            assert get_result.content["issueKey"] == issue_key
            # 3. 課題更新
            update_result = await session.call_tool(
                "update_issue",
                {"issue_id_or_key": issue_key, "summary": "MCP E2Eテスト課題(更新)"}
            )
            assert hasattr(update_result, "content")
            assert update_result.content["summary"] == "MCP E2Eテスト課題(更新)"
            # 4. コメント追加
            comment_result = await session.call_tool(
                "add_comment",
                {"issue_id_or_key": issue_key, "content": "MCP E2Eテストコメント"}
            )
            assert hasattr(comment_result, "content")
            assert comment_result.content["content"] == "MCP E2Eテストコメント"
            # 5. コメント一覧取得
            comments_result = await session.call_tool(
                "get_issue_comments",
                {"issue_id_or_key": issue_key}
            )
            assert hasattr(comments_result, "content")
            assert any(c["content"] == "MCP E2Eテストコメント" for c in comments_result.content)
            # 6. 課題削除
            delete_result = await session.call_tool("delete_issue", {"issue_id_or_key": issue_key})
            assert hasattr(delete_result, "content")
            assert delete_result.content is True or delete_result.content is None

@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE") or not os.getenv("BACKLOG_PROJECT"),
    reason="Backlog API環境変数が設定されていません"
)
async def test_mcp_client_create_with_name_parameters(mcp_server_url):
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
                    "description": "名前ベースのパラメータによるMCPクライアントSDK経由E2Eテスト課題"
                }
            )
            assert hasattr(create_result, "content")
            issue_key = create_result.content["issueKey"]
            # 課題取得
            get_result = await session.call_tool("get_issue", {"issue_id_or_key": issue_key})
            assert hasattr(get_result, "content")
            assert get_result.content["issueKey"] == issue_key
            assert get_result.content["summary"] == "名前ベースのMCP E2Eテスト課題"
            # 課題削除
            delete_result = await session.call_tool("delete_issue", {"issue_id_or_key": issue_key})
            assert hasattr(delete_result, "content")
            assert delete_result.content is True or delete_result.content is None

@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE") or not os.getenv("BACKLOG_PROJECT"),
    reason="Backlog API環境変数が設定されていません"
)
async def test_mcp_client_update_with_name_parameters(mcp_server_url):
    """名前ベースのパラメータで課題を更新するMCPクライアントSDK経由E2Eテスト"""
    project_key = os.getenv("BACKLOG_PROJECT")
    # 課題作成→名前ベースで更新→削除
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # 課題種別ID取得
            types_result = await session.call_tool("get_issue_types", {"project_key": project_key})
            assert hasattr(types_result, "content")
            issue_type_id = types_result.content[0]["id"]
            # 課題作成
            create_result = await session.call_tool(
                "create_issue",
                {
                    "project_key": project_key,
                    "summary": "更新用MCP E2Eテスト課題",
                    "issue_type_id": issue_type_id,
                    "priority_id": 3,
                    "description": "名前ベースで更新するMCPクライアントSDK経由E2Eテスト課題"
                }
            )
            assert hasattr(create_result, "content")
            issue_key = create_result.content["issueKey"]
            # 名前ベースで課題更新
            update_result = await session.call_tool(
                "update_issue",
                {
                    "issue_id_or_key": issue_key,
                    "summary": "名前ベースで更新されたMCP E2Eテスト課題",
                    "status_name": "処理中",  # ステータス名で指定
                    "priority_name": "高"  # 優先度名で指定
                }
            )
            assert hasattr(update_result, "content")
            assert update_result.content["summary"] == "名前ベースで更新されたMCP E2Eテスト課題"
            # 課題削除
            delete_result = await session.call_tool("delete_issue", {"issue_id_or_key": issue_key})
            assert hasattr(delete_result, "content")
            assert delete_result.content is True or delete_result.content is None
