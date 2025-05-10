"""
一括操作のMCPツール
"""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp.types import Tool

from app.application.services.bulk_operations_service import BulkOperationsService
from app.infrastructure.backlog.backlog_client_wrapper import BacklogClientWrapper
from app.core.config import settings

# 環境変数の読み込み
load_dotenv()


def get_bulk_operations_service() -> BulkOperationsService:
    """
    一括操作サービスのインスタンスを取得

    Returns:
        BulkOperationsService: 一括操作サービス
    """
    api_key = os.getenv("BACKLOG_API_KEY")
    space = os.getenv("BACKLOG_SPACE")

    if not api_key or not space:
        raise ValueError(
            "Backlog API configuration is missing. Please set BACKLOG_API_KEY and BACKLOG_SPACE environment variables."
        )

    backlog_client = BacklogClientWrapper(api_key=api_key, space=space, read_only_mode=settings.READ_ONLY_MODE)
    return BulkOperationsService(backlog_client=backlog_client)


# 複数チケットのステータスを一括更新するMCPツール
bulk_update_status_tool = Tool(
    name="bulk_update_status",
    description="複数のBacklogチケットのステータスを一括更新します",
    inputSchema={
        "type": "object",
        "properties": {
            "issue_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "課題IDまたは課題キーのリスト",
            },
            "status_id": {"type": "integer", "description": "更新後のステータスID"},
        },
        "required": ["issue_ids", "status_id"],
    },
)


# @bulk_update_status_tool.handler
async def bulk_update_status_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    複数チケットのステータスを一括更新するMCPツールのハンドラー

    Args:
        params: パラメータ
            - issue_ids: 課題IDまたは課題キーのリスト
            - status_id: 更新後のステータスID

    Returns:
        処理結果の統計情報
    """
    issue_ids = params.get("issue_ids", [])
    status_id = params.get("status_id")

    if not issue_ids:
        raise ValueError("issue_ids is required")
    if status_id is None:
        raise ValueError("status_id is required")

    bulk_service = get_bulk_operations_service()
    return bulk_service.bulk_update_status(issue_ids=issue_ids, status_id=status_id)


# 複数チケットの担当者を一括更新するMCPツール
bulk_update_assignee_tool = Tool(
    name="bulk_update_assignee",
    description="複数のBacklogチケットの担当者を一括更新します",
    inputSchema={
        "type": "object",
        "properties": {
            "issue_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "課題IDまたは課題キーのリスト",
            },
            "assignee_id": {"type": "integer", "description": "更新後の担当者ID"},
        },
        "required": ["issue_ids", "assignee_id"],
    },
)


# @bulk_update_assignee_tool.handler
async def bulk_update_assignee_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    複数チケットの担当者を一括更新するMCPツールのハンドラー

    Args:
        params: パラメータ
            - issue_ids: 課題IDまたは課題キーのリスト
            - assignee_id: 更新後の担当者ID

    Returns:
        処理結果の統計情報
    """
    issue_ids = params.get("issue_ids", [])
    assignee_id = params.get("assignee_id")

    if not issue_ids:
        raise ValueError("issue_ids is required")
    if assignee_id is None:
        raise ValueError("assignee_id is required")

    bulk_service = get_bulk_operations_service()
    return bulk_service.bulk_update_assignee(
        issue_ids=issue_ids, assignee_id=assignee_id
    )


# 複数チケットの優先度を一括更新するMCPツール
bulk_update_priority_tool = Tool(
    name="bulk_update_priority",
    description="複数のBacklogチケットの優先度を一括更新します",
    inputSchema={
        "type": "object",
        "properties": {
            "issue_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "課題IDまたは課題キーのリスト",
            },
            "priority_id": {"type": "integer", "description": "更新後の優先度ID"},
        },
        "required": ["issue_ids", "priority_id"],
    },
)


# @bulk_update_priority_tool.handler
async def bulk_update_priority_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    複数チケットの優先度を一括更新するMCPツールのハンドラー

    Args:
        params: パラメータ
            - issue_ids: 課題IDまたは課題キーのリスト
            - priority_id: 更新後の優先度ID

    Returns:
        処理結果の統計情報
    """
    issue_ids = params.get("issue_ids", [])
    priority_id = params.get("priority_id")

    if not issue_ids:
        raise ValueError("issue_ids is required")
    if priority_id is None:
        raise ValueError("priority_id is required")

    bulk_service = get_bulk_operations_service()
    return bulk_service.bulk_update_priority(
        issue_ids=issue_ids, priority_id=priority_id
    )


# 複数チケットのマイルストーンを一括更新するMCPツール
bulk_update_milestone_tool = Tool(
    name="bulk_update_milestone",
    description="複数のBacklogチケットのマイルストーンを一括更新します",
    inputSchema={
        "type": "object",
        "properties": {
            "issue_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "課題IDまたは課題キーのリスト",
            },
            "milestone_id": {
                "type": "integer",
                "description": "更新後のマイルストーンID",
            },
        },
        "required": ["issue_ids", "milestone_id"],
    },
)


# @bulk_update_milestone_tool.handler
async def bulk_update_milestone_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    複数チケットのマイルストーンを一括更新するMCPツールのハンドラー

    Args:
        params: パラメータ
            - issue_ids: 課題IDまたは課題キーのリスト
            - milestone_id: 更新後のマイルストーンID

    Returns:
        処理結果の統計情報
    """
    issue_ids = params.get("issue_ids", [])
    milestone_id = params.get("milestone_id")

    if not issue_ids:
        raise ValueError("issue_ids is required")
    if milestone_id is None:
        raise ValueError("milestone_id is required")

    bulk_service = get_bulk_operations_service()
    return bulk_service.bulk_update_milestone(
        issue_ids=issue_ids, milestone_id=milestone_id
    )


# 複数チケットのカテゴリを一括更新するMCPツール
bulk_update_category_tool = Tool(
    name="bulk_update_category",
    description="複数のBacklogチケットのカテゴリを一括更新します",
    inputSchema={
        "type": "object",
        "properties": {
            "issue_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "課題IDまたは課題キーのリスト",
            },
            "category_id": {"type": "integer", "description": "更新後のカテゴリID"},
        },
        "required": ["issue_ids", "category_id"],
    },
)


# @bulk_update_category_tool.handler
async def bulk_update_category_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    複数チケットのカテゴリを一括更新するMCPツールのハンドラー

    Args:
        params: パラメータ
            - issue_ids: 課題IDまたは課題キーのリスト
            - category_id: 更新後のカテゴリID

    Returns:
        処理結果の統計情報
    """
    issue_ids = params.get("issue_ids", [])
    category_id = params.get("category_id")

    if not issue_ids:
        raise ValueError("issue_ids is required")
    if category_id is None:
        raise ValueError("category_id is required")

    bulk_service = get_bulk_operations_service()
    return bulk_service.bulk_update_category(
        issue_ids=issue_ids, category_id=category_id
    )


# 複数チケットを一括削除するMCPツール
bulk_delete_issues_tool = Tool(
    name="bulk_delete_issues",
    description="複数のBacklogチケットを一括削除します",
    inputSchema={
        "type": "object",
        "properties": {
            "issue_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "課題IDまたは課題キーのリスト",
            }
        },
        "required": ["issue_ids"],
    },
)


# @bulk_delete_issues_tool.handler
async def bulk_delete_issues_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    複数チケットを一括削除するMCPツールのハンドラー

    Args:
        params: パラメータ
            - issue_ids: 課題IDまたは課題キーのリスト

    Returns:
        処理結果の統計情報
    """
    issue_ids = params.get("issue_ids", [])

    if not issue_ids:
        raise ValueError("issue_ids is required")

    bulk_service = get_bulk_operations_service()
    return bulk_service.bulk_delete_issues(issue_ids=issue_ids)
