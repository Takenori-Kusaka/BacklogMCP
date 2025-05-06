"""
プロジェクト管理のエンドツーエンドテスト
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
async def test_get_projects_from_real_api(mcp_server_url: str) -> None:
    """FastAPIサーバー経由でプロジェクト一覧を取得するE2Eテスト"""
    # MCP Client SDKを使用してプロジェクト一覧を取得
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # プロジェクト一覧取得
            result = await session.call_tool("get_projects", {})
            assert hasattr(result, "content")
            
            # MCPのレスポンスはTextContent | ImageContent | EmbeddedResourceの配列
            # TextContentの場合はJSON文字列をパースする必要がある
            if result.content and len(result.content) > 0:
                content_item = result.content[0]
                if hasattr(content_item, "text"):
                    # JSONをパース
                    import json
                    projects = json.loads(content_item.text)
                    assert isinstance(projects, list)
                    # プロジェクトが存在する場合のみ検証
                    if projects:
                        assert "id" in projects[0]
                        assert "projectKey" in projects[0]
                        assert "name" in projects[0]


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY")
    or not os.getenv("BACKLOG_SPACE")
    or not os.getenv("BACKLOG_PROJECT"),
    reason="Backlog API環境変数が設定されていません",
)
async def test_get_project_by_key(mcp_server_url: str) -> None:
    """FastAPIサーバー経由で特定のプロジェクトを取得するE2Eテスト"""
    project_key = os.getenv("BACKLOG_PROJECT")

    # MCP Client SDKを使用して特定のプロジェクトを取得
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # 特定のプロジェクト取得
            result = await session.call_tool(
                "get_project", {"project_key": project_key}
            )
            assert hasattr(result, "content")
            
            # MCPのレスポンスはTextContent | ImageContent | EmbeddedResourceの配列
            # TextContentの場合はJSON文字列をパースする必要がある
            if result.content and len(result.content) > 0:
                content_item = result.content[0]
                if hasattr(content_item, "text"):
                    # JSONをパース
                    import json
                    project = json.loads(content_item.text)
                    assert isinstance(project, dict)
                    assert "id" in project
                    assert "projectKey" in project
                    assert project["projectKey"] == project_key
