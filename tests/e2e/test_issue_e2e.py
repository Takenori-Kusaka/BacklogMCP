"""
課題管理のエンドツーエンドテスト
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
    not os.getenv("BACKLOG_API_KEY")
    or not os.getenv("BACKLOG_SPACE")
    or not os.getenv("BACKLOG_PROJECT"),
    reason="Backlog API環境変数が設定されていません",
)
async def test_get_issues_from_real_api(mcp_server_url: str) -> None:
    """FastAPIサーバー経由で課題一覧を取得するE2Eテスト"""
    # MCP Client SDKを使用して課題一覧を取得
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # 課題一覧取得
            result = await session.call_tool("get_issues", {})
            assert hasattr(result, "content")
            assert isinstance(result.content, list)
            # 課題が存在する場合のみ検証
            if result.content:
                assert "id" in result.content[0]
                assert "issueKey" in result.content[0]
                assert "summary" in result.content[0]


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY")
    or not os.getenv("BACKLOG_SPACE")
    or not os.getenv("BACKLOG_PROJECT"),
    reason="Backlog API環境変数が設定されていません",
)
async def test_get_issue_by_key(mcp_server_url: str) -> None:
    """FastAPIサーバー経由で特定の課題を取得するE2Eテスト"""
    project_key = os.getenv("BACKLOG_PROJECT")

    # MCP Client SDKを使用して課題を作成・取得・削除
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 課題種別ID取得
            types_result = await session.call_tool(
                "get_issue_types", {"project_key": project_key}
            )
            assert hasattr(types_result, "content")
            issue_type_id = types_result.content[0]["id"]

            # 課題作成
            create_result = await session.call_tool(
                "create_issue",
                {
                    "project_id": None,  # project_keyで十分
                    "project_key": project_key,
                    "summary": "E2Eテスト用課題",
                    "issue_type_id": issue_type_id,
                    "priority_id": 3,
                    "description": "これはE2Eテスト用の課題です。",
                },
            )
            assert hasattr(create_result, "content")
            issue_key = create_result.content["issueKey"]

            try:
                # 課題取得
                get_result = await session.call_tool(
                    "get_issue", {"issue_id_or_key": issue_key}
                )
                assert hasattr(get_result, "content")
                assert get_result.content["issueKey"] == issue_key
                assert get_result.content["summary"] == "E2Eテスト用課題"
            finally:
                # 課題削除（クリーンアップ）
                delete_result = await session.call_tool(
                    "delete_issue", {"issue_id_or_key": issue_key}
                )
                assert hasattr(delete_result, "content")
                assert delete_result.content is True or delete_result.content is None


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY")
    or not os.getenv("BACKLOG_SPACE")
    or not os.getenv("BACKLOG_PROJECT"),
    reason="Backlog API環境変数が設定されていません",
)
async def test_create_issue_with_name_parameters(mcp_server_url: str) -> None:
    """名前ベースのパラメータで課題を作成するE2Eテスト"""
    project_key = os.getenv("BACKLOG_PROJECT")

    # MCP Client SDKを使用して課題を作成・削除
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 課題作成（名前ベースのパラメータ）
            create_result = await session.call_tool(
                "create_issue",
                {
                    "project_key": project_key,
                    "summary": "名前ベースのE2Eテスト用課題",
                    "issue_type_name": "タスク",  # 課題種別名で指定
                    "priority_name": "中",  # 優先度名で指定
                    "description": "これは名前ベースのパラメータによるE2Eテスト用の課題です。",
                },
            )
            assert hasattr(create_result, "content")
            issue_key = create_result.content["issueKey"]

            try:
                # 課題取得
                get_result = await session.call_tool(
                    "get_issue", {"issue_id_or_key": issue_key}
                )
                assert hasattr(get_result, "content")
                assert get_result.content["issueKey"] == issue_key
                assert get_result.content["summary"] == "名前ベースのE2Eテスト用課題"
            finally:
                # 課題削除（クリーンアップ）
                delete_result = await session.call_tool(
                    "delete_issue", {"issue_id_or_key": issue_key}
                )
                assert hasattr(delete_result, "content")
                assert delete_result.content is True or delete_result.content is None


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY")
    or not os.getenv("BACKLOG_SPACE")
    or not os.getenv("BACKLOG_PROJECT"),
    reason="Backlog API環境変数が設定されていません",
)
async def test_update_issue(mcp_server_url: str) -> None:
    """FastAPIサーバー経由で課題を更新するE2Eテスト"""
    project_key = os.getenv("BACKLOG_PROJECT")

    # MCP Client SDKを使用して課題を作成・更新・削除
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 課題種別ID取得
            types_result = await session.call_tool(
                "get_issue_types", {"project_key": project_key}
            )
            assert hasattr(types_result, "content")
            issue_type_id = types_result.content[0]["id"]

            # 課題作成
            create_result = await session.call_tool(
                "create_issue",
                {
                    "project_id": None,  # project_keyで十分
                    "project_key": project_key,
                    "summary": "E2Eテスト用課題（更新テスト）",
                    "issue_type_id": issue_type_id,
                    "priority_id": 3,
                    "description": "これはE2Eテスト用の課題です。",
                },
            )
            assert hasattr(create_result, "content")
            issue_key = create_result.content["issueKey"]

            try:
                # 課題更新
                update_result = await session.call_tool(
                    "update_issue",
                    {
                        "issue_id_or_key": issue_key,
                        "summary": "更新されたE2Eテスト用課題",
                    },
                )
                assert hasattr(update_result, "content")
                assert update_result.content["issueKey"] == issue_key
                assert update_result.content["summary"] == "更新されたE2Eテスト用課題"

                # 更新された課題を取得して確認
                get_result = await session.call_tool(
                    "get_issue", {"issue_id_or_key": issue_key}
                )
                assert hasattr(get_result, "content")
                assert get_result.content["issueKey"] == issue_key
                assert get_result.content["summary"] == "更新されたE2Eテスト用課題"
            finally:
                # 課題削除（クリーンアップ）
                delete_result = await session.call_tool(
                    "delete_issue", {"issue_id_or_key": issue_key}
                )
                assert hasattr(delete_result, "content")
                assert delete_result.content is True or delete_result.content is None


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY")
    or not os.getenv("BACKLOG_SPACE")
    or not os.getenv("BACKLOG_PROJECT"),
    reason="Backlog API環境変数が設定されていません",
)
async def test_update_issue_with_name_parameters(mcp_server_url: str) -> None:
    """名前ベースのパラメータで課題を更新するE2Eテスト"""
    project_key = os.getenv("BACKLOG_PROJECT")

    # MCP Client SDKを使用して課題を作成・更新・削除
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 課題種別ID取得
            types_result = await session.call_tool(
                "get_issue_types", {"project_key": project_key}
            )
            assert hasattr(types_result, "content")
            issue_type_id = types_result.content[0]["id"]

            # 課題作成
            create_result = await session.call_tool(
                "create_issue",
                {
                    "project_key": project_key,
                    "summary": "名前ベースで更新するE2Eテスト用課題",
                    "issue_type_id": issue_type_id,
                    "priority_id": 3,
                    "description": "これは名前ベースで更新するE2Eテスト用の課題です。",
                },
            )
            assert hasattr(create_result, "content")
            issue_key = create_result.content["issueKey"]

            try:
                # 課題更新（名前ベースのパラメータ）
                update_result = await session.call_tool(
                    "update_issue",
                    {
                        "issue_id_or_key": issue_key,
                        "summary": "名前ベースで更新されたE2Eテスト用課題",
                        "status_name": "処理中",  # ステータス名で指定
                        "priority_name": "高",  # 優先度名で指定
                        "assignee_name": "テストユーザー",  # 担当者名で指定（実際の環境に合わせて調整が必要）
                    },
                )
                assert hasattr(update_result, "content")
                assert update_result.content["issueKey"] == issue_key
                assert (
                    update_result.content["summary"]
                    == "名前ベースで更新されたE2Eテスト用課題"
                )

                # 更新された課題を取得して確認
                get_result = await session.call_tool(
                    "get_issue", {"issue_id_or_key": issue_key}
                )
                assert hasattr(get_result, "content")
                assert get_result.content["issueKey"] == issue_key
                assert (
                    get_result.content["summary"]
                    == "名前ベースで更新されたE2Eテスト用課題"
                )
            finally:
                # 課題削除（クリーンアップ）
                delete_result = await session.call_tool(
                    "delete_issue", {"issue_id_or_key": issue_key}
                )
                assert hasattr(delete_result, "content")
                assert delete_result.content is True or delete_result.content is None


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY")
    or not os.getenv("BACKLOG_SPACE")
    or not os.getenv("BACKLOG_PROJECT"),
    reason="Backlog API環境変数が設定されていません",
)
async def test_add_and_get_comments(mcp_server_url: str) -> None:
    """FastAPIサーバー経由でコメントを追加して取得するE2Eテスト"""
    project_key = os.getenv("BACKLOG_PROJECT")

    # MCP Client SDKを使用して課題を作成・コメント追加・削除
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 課題種別ID取得
            types_result = await session.call_tool(
                "get_issue_types", {"project_key": project_key}
            )
            assert hasattr(types_result, "content")
            issue_type_id = types_result.content[0]["id"]

            # 課題作成
            create_result = await session.call_tool(
                "create_issue",
                {
                    "project_id": None,  # project_keyで十分
                    "project_key": project_key,
                    "summary": "E2Eテスト用課題（コメントテスト）",
                    "issue_type_id": issue_type_id,
                    "priority_id": 3,
                    "description": "これはE2Eテスト用の課題です。",
                },
            )
            assert hasattr(create_result, "content")
            issue_key = create_result.content["issueKey"]

            try:
                # コメント追加
                comment_result = await session.call_tool(
                    "add_comment",
                    {
                        "issue_id_or_key": issue_key,
                        "content": "これはE2Eテスト用のコメントです。",
                    },
                )
                assert hasattr(comment_result, "content")
                assert (
                    comment_result.content["content"]
                    == "これはE2Eテスト用のコメントです。"
                )

                # コメント一覧取得
                comments_result = await session.call_tool(
                    "get_issue_comments", {"issue_id_or_key": issue_key}
                )
                assert hasattr(comments_result, "content")
                assert isinstance(comments_result.content, list)
                assert len(comments_result.content) > 0
                assert any(
                    c["content"] == "これはE2Eテスト用のコメントです。"
                    for c in comments_result.content
                )
            finally:
                # 課題削除（クリーンアップ）
                delete_result = await session.call_tool(
                    "delete_issue", {"issue_id_or_key": issue_key}
                )
                assert hasattr(delete_result, "content")
                assert delete_result.content is True or delete_result.content is None


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.getenv("BACKLOG_API_KEY")
    or not os.getenv("BACKLOG_SPACE")
    or not os.getenv("BACKLOG_PROJECT"),
    reason="Backlog API環境変数が設定されていません",
)
async def test_create_and_delete_issue(mcp_server_url: str) -> None:
    """FastAPIサーバー経由で課題を作成して削除するE2Eテスト"""
    project_key = os.getenv("BACKLOG_PROJECT")

    # MCP Client SDKを使用して課題を作成・削除
    async with sse_client(mcp_server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 課題種別ID取得
            types_result = await session.call_tool(
                "get_issue_types", {"project_key": project_key}
            )
            assert hasattr(types_result, "content")
            issue_type_id = types_result.content[0]["id"]

            # 課題作成
            create_result = await session.call_tool(
                "create_issue",
                {
                    "project_id": None,  # project_keyで十分
                    "project_key": project_key,
                    "summary": "E2Eテスト用課題（削除テスト）",
                    "issue_type_id": issue_type_id,
                    "priority_id": 3,
                    "description": "これはE2Eテスト用の課題です。",
                },
            )
            assert hasattr(create_result, "content")
            issue_key = create_result.content["issueKey"]

            # 課題削除
            delete_result = await session.call_tool(
                "delete_issue", {"issue_id_or_key": issue_key}
            )
            assert hasattr(delete_result, "content")
            assert delete_result.content is True or delete_result.content is None

            # 削除されたことを確認
            try:
                get_result = await session.call_tool(
                    "get_issue", {"issue_id_or_key": issue_key}
                )
                # 削除されていれば例外が発生するはず
                assert False, "削除されたはずの課題が取得できました"
            except Exception as e:
                # 例外が発生することを確認
                assert "not found" in str(e).lower() or "error" in str(e).lower()
