"""
MCP経由のプロジェクト管理E2Eテスト
"""

import asyncio
import json
import os

import httpx
import pytest
from mcp.client.session import ClientSession

from tests.e2e.mcp_client_utils import create_mcp_client_session
from tests.logger_config import setup_logger

# テスト用のロガー
logger = setup_logger("test_project_mcp_e2e", "test_project_mcp_e2e.log")


@pytest.mark.asyncio
@pytest.mark.timeout(60)  # 60秒でタイムアウト
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE"),
    reason="Backlog API環境変数が設定されていません",
)
async def test_mcp_get_projects(mcp_server_url: str) -> None:
    """MCP経由でプロジェクト一覧を取得するテスト"""
    logger.info(f"テスト開始: test_mcp_get_projects")
    logger.info(f"MCP Server URL: {mcp_server_url}")

    # MCP Client SDKを使用してプロジェクト一覧を取得
    logger.info(f"SSEクライアント接続開始")

    # SSEクライアントの接続をデバッグ
    try:
        # 直接HTTPリクエストを送信してMCPエンドポイントをチェック
        import requests

        logger.info(f"MCPエンドポイントの直接チェック: {mcp_server_url}/mcp")
        response = requests.get(f"{mcp_server_url}/mcp", stream=True)
        logger.info(f"MCPエンドポイントのステータスコード: {response.status_code}")
        logger.info(
            f"MCPエンドポイントのContent-Type: {response.headers.get('Content-Type')}"
        )
        # 最初の数バイトだけ読み取る
        first_chunk = next(response.iter_content(chunk_size=100), None)
        logger.info(f"MCPエンドポイントの最初のチャンク: {first_chunk}")
        response.close()
    except Exception as e:
        logger.error(f"MCPエンドポイントのチェック中にエラーが発生: {str(e)}")

    # カスタムSSEクライアントを使用してMCPクライアントセッションを作成
    try:
        # MCPクライアントセッションを作成
        logger.info(f"MCPクライアントセッション作成開始")
        session = await create_mcp_client_session(mcp_server_url)
        logger.info(f"MCPクライアントセッション作成完了")

        # 利用可能なツール一覧を取得
        logger.info(f"利用可能なツール一覧を取得")
        tools_result = await session.list_tools()
        logger.info(
            f"利用可能なツール一覧: {[tool.name for tool in tools_result.tools]}"
        )

        # プロジェクト一覧取得
        # FastApiMCP 0.3.3では、FastAPIのエンドポイントのoperation_idがMCPツールの名前として使用される
        # しかし、実際には異なる名前が使用される可能性がある
        # 可能性のある名前を順番に試す
        tool_names = [
            "get_projects",
            "api_projects__get",
            "api/projects/",
            "api/projects",
        ]

        # 利用可能なツール一覧から、最も近いツール名を追加
        for tool in tools_result.tools:
            if "project" in tool.name.lower() and tool.name not in tool_names:
                tool_names.insert(0, tool.name)

        logger.info(f"試行するツール名一覧: {tool_names}")

        for tool_name in tool_names:
            try:
                logger.info(f"ツール名試行: {tool_name}")
                result = await session.call_tool(tool_name, {})
                logger.info(f"成功したツール名: {tool_name}")
                logger.info(f"結果: {result}")
                break
            except Exception as e:
                logger.error(f"ツール名 {tool_name} は失敗: {str(e)}")
                if tool_name == tool_names[-1]:  # 最後のツール名
                    logger.error(f"すべてのツール名が失敗")
                    raise Exception(f"すべてのツール名が失敗しました: {str(e)}")

            logger.info(f"結果検証開始")
            assert hasattr(result, "content")
            assert isinstance(result.content, list)
            if result.content:
                # TextContentからJSONをパース
                import json

                text_content = result.content[0]
                assert hasattr(text_content, "text")
                project_data = json.loads(text_content.text)

                # プロジェクトデータを検証
                assert "projectKey" in project_data
                assert "name" in project_data
            logger.info(f"テスト完了: test_mcp_get_projects")
    except Exception as e:
        logger.error(f"SSEクライアントの接続中にエラーが発生: {str(e)}")
        raise


@pytest.mark.asyncio
@pytest.mark.timeout(60)  # 60秒でタイムアウト
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY")
    or not os.getenv("BACKLOG_SPACE")
    or not os.getenv("BACKLOG_PROJECT"),
    reason="Backlog API環境変数が設定されていません",
)
async def test_mcp_get_project_by_key(mcp_server_url: str) -> None:
    """MCP経由で特定プロジェクトを取得するテスト"""
    logger.info(f"テスト開始: test_mcp_get_project_by_key")
    project_key = os.getenv("BACKLOG_PROJECT")
    logger.info(f"プロジェクトキー: {project_key}")
    logger.info(f"MCP Server URL: {mcp_server_url}")

    # MCP Client SDKを使用して特定プロジェクトを取得
    logger.info(f"SSEクライアント接続開始")

    # カスタムSSEクライアントを使用してMCPクライアントセッションを作成
    try:
        # MCPクライアントセッションを作成
        logger.info(f"MCPクライアントセッション作成開始")
        session = await create_mcp_client_session(mcp_server_url)
        logger.info(f"MCPクライアントセッション作成完了")

        # 利用可能なツール一覧を取得
        logger.info(f"利用可能なツール一覧を取得")
        tools_result = await session.list_tools()
        logger.info(
            f"利用可能なツール一覧: {[tool.name for tool in tools_result.tools]}"
        )

        # 特定プロジェクト取得
        # FastApiMCP 0.3.3では、FastAPIのエンドポイントのoperation_idがMCPツールの名前として使用される
        # しかし、実際には異なる名前が使用される可能性がある
        # 可能性のある名前を順番に試す
        tool_names = [
            "get_project",
            "api_projects__project_key__get",
            "api/projects/{project_key}",
            "api/projects/{project_key}/",
        ]

        # 利用可能なツール一覧から、最も近いツール名を追加
        for tool in tools_result.tools:
            if (
                "project" in tool.name.lower()
                and "key" in tool.name.lower()
                and tool.name not in tool_names
            ):
                tool_names.insert(0, tool.name)

        logger.info(f"試行するツール名一覧: {tool_names}")

        for tool_name in tool_names:
            try:
                logger.info(f"ツール名試行: {tool_name}")
                result = await session.call_tool(
                    tool_name, {"project_key": project_key}
                )
                logger.info(f"成功したツール名: {tool_name}")
                logger.info(f"結果: {result}")
                break
            except Exception as e:
                logger.error(f"ツール名 {tool_name} は失敗: {str(e)}")
                if tool_name == tool_names[-1]:  # 最後のツール名
                    logger.error(f"すべてのツール名が失敗")
                    raise Exception(f"すべてのツール名が失敗しました: {str(e)}")

        logger.info(f"結果検証開始")
        assert hasattr(result, "content")
        assert isinstance(result.content, list)
        if result.content:
            # TextContentからJSONをパース
            import json

            text_content = result.content[0]
            assert hasattr(text_content, "text")
            project_data = json.loads(text_content.text)

            # プロジェクトデータを検証
            assert "projectKey" in project_data
            assert project_data["projectKey"] == project_key
        logger.info(f"テスト完了: test_mcp_get_project_by_key")
    except Exception as e:
        logger.error(f"SSEクライアントの接続中にエラーが発生: {str(e)}")
        raise
