"""
MCPクライアントSDK経由でBacklogユースケース（課題一括操作）E2Eテスト
"""
import os
import asyncio
import pytest
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE"),
    reason="Backlog API環境変数が設定されていません"
)
async def test_mcp_client_bulk_update_status(mcp_server_url):
    """MCPクライアントSDK経由で複数課題のステータス一括更新ユースケース"""
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # ユースケース: 一括ステータス変更
            result = await session.call_tool(
                "bulk_update_status",
                {"issue_ids": ["TEST-1", "TEST-2", "TEST-3"], "status_id": 2}
            )
            assert hasattr(result, "content")
            assert result.content["total"] == 3
            assert result.content["success"] + result.content["failed"] == result.content["total"]
            assert len(result.content["failed_issues"]) == result.content["failed"]

@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE"),
    reason="Backlog API環境変数が設定されていません"
)
async def test_mcp_client_bulk_delete_issues(mcp_server_url):
    """MCPクライアントSDK経由で複数課題の一括削除ユースケース"""
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # ユースケース: 一括削除
            result = await session.call_tool(
                "bulk_delete_issues",
                {"issue_ids": ["TEST-4", "TEST-5", "TEST-6"]}
            )
            assert hasattr(result, "content")
            assert result.content["total"] == 3
            assert result.content["success"] + result.content["failed"] == result.content["total"]
            assert len(result.content["failed_issues"]) == result.content["failed"]
