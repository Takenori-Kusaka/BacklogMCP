"""
MCP経由の一括操作E2Eテスト
"""
import os
import pytest
import json
import httpx
import asyncio
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE"),
    reason="Backlog API環境変数が設定されていません"
)
async def test_mcp_bulk_update_status(mcp_server_url):
    """MCP経由で複数チケットのステータスを一括更新するテスト"""
    # MCP Client SDKを使用して複数チケットのステータスを一括更新
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # 一括ステータス更新
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
async def test_mcp_bulk_delete_issues(mcp_server_url):
    """MCP経由で複数チケットを一括削除するテスト"""
    # MCP Client SDKを使用して複数チケットを一括削除
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # 一括削除
            result = await session.call_tool(
                "bulk_delete_issues",
                {"issue_ids": ["TEST-4", "TEST-5", "TEST-6"]}
            )
            assert hasattr(result, "content")
            assert result.content["total"] == 3
            assert result.content["success"] + result.content["failed"] == result.content["total"]
            assert len(result.content["failed_issues"]) == result.content["failed"]

@pytest.mark.asyncio
async def test_mcp_bulk_update_status_invalid_request(mcp_server_url):
    """MCP経由で不正なリクエストボディのバリデーションテスト"""
    # MCP Client SDKを使用して不正なリクエストを送信
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # 必須パラメータが欠けている
            try:
                await session.call_tool(
                    "bulk_update_status",
                    {"issue_ids": ["TEST-1", "TEST-2", "TEST-3"]}  # status_idが欠けている
                )
                assert False, "必須パラメータが欠けているのに例外が発生しませんでした"
            except Exception as e:
                assert "status_id" in str(e).lower() or "required" in str(e).lower()
            
            # 不正な型のパラメータ
            try:
                await session.call_tool(
                    "bulk_update_status",
                    {"issue_ids": ["TEST-1", "TEST-2", "TEST-3"], "status_id": "invalid"}
                )
                assert False, "不正な型のパラメータなのに例外が発生しませんでした"
            except Exception as e:
                assert "status_id" in str(e).lower() or "type" in str(e).lower()
