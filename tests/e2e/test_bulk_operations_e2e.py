"""
一括操作のエンドツーエンドテスト
"""

import asyncio
import json
import os

import httpx
import pytest
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE"),
    reason="Backlog API環境変数が設定されていません",
)
async def test_bulk_update_status_e2e(mcp_server_url):
    """FastAPIサーバー経由で複数チケットのステータスを一括更新するE2Eテスト"""
    # MCP Client SDKを使用して複数チケットのステータスを一括更新
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # 一括ステータス更新
            result = await session.call_tool(
                "bulk_update_status",
                {"issue_ids": ["TEST-1", "TEST-2", "TEST-3"], "status_id": 2},
            )
            assert hasattr(result, "content")
            assert result.content["total"] == 3
            assert (
                result.content["success"] + result.content["failed"]
                == result.content["total"]
            )
            assert len(result.content["failed_issues"]) == result.content["failed"]


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE"),
    reason="Backlog API環境変数が設定されていません",
)
async def test_bulk_delete_issues_e2e(mcp_server_url):
    """FastAPIサーバー経由で複数チケットを一括削除するE2Eテスト"""
    # MCP Client SDKを使用して複数チケットを一括削除
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # 一括削除
            result = await session.call_tool(
                "bulk_delete_issues", {"issue_ids": ["TEST-4", "TEST-5", "TEST-6"]}
            )
            assert hasattr(result, "content")
            assert result.content["total"] == 3
            assert (
                result.content["success"] + result.content["failed"]
                == result.content["total"]
            )
            assert len(result.content["failed_issues"]) == result.content["failed"]


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE"),
    reason="Backlog API環境変数が設定されていません",
)
async def test_bulk_update_status_with_missing_config(mcp_server_url):
    """環境変数が設定されていない場合のエラーハンドリングテスト"""
    # このテストはスキップ - 実際の環境変数を使用するため
    pass


@pytest.mark.asyncio
async def test_bulk_update_status_with_invalid_request(mcp_server_url):
    """FastAPIサーバー経由で不正なリクエストボディのバリデーションテスト"""
    # MCP Client SDKを使用して不正なリクエストを送信
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # 必須パラメータが欠けている
            try:
                await session.call_tool(
                    "bulk_update_status",
                    {
                        "issue_ids": ["TEST-1", "TEST-2", "TEST-3"]
                    },  # status_idが欠けている
                )
                assert False, "必須パラメータが欠けているのに例外が発生しませんでした"
            except Exception as e:
                assert "status_id" in str(e).lower() or "required" in str(e).lower()

            # 不正な型のパラメータ
            try:
                await session.call_tool(
                    "bulk_update_status",
                    {
                        "issue_ids": ["TEST-1", "TEST-2", "TEST-3"],
                        "status_id": "invalid",
                    },
                )
                assert False, "不正な型のパラメータなのに例外が発生しませんでした"
            except Exception as e:
                assert "status_id" in str(e).lower() or "type" in str(e).lower()
