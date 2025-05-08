"""
一括操作のAPIエンドポイント
"""

import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.application.services.bulk_operations_service import BulkOperationsService
from app.infrastructure.backlog.backlog_client import BacklogClient # 正しくは backlog_client_wrapper を使うべき
from app.core.config import settings # settings をインポート

# 環境変数の読み込み
load_dotenv()

# ルーターの作成
router = APIRouter(
    prefix="/api/bulk",
    tags=["bulk_operations"],
    responses={404: {"description": "Not found"}},
)


# リクエストボディのモデル
class BulkUpdateRequest(BaseModel):
    """一括更新リクエスト"""

    issue_ids: List[str]


class BulkStatusUpdateRequest(BulkUpdateRequest):
    """ステータス一括更新リクエスト"""

    status_id: int


class BulkAssigneeUpdateRequest(BulkUpdateRequest):
    """担当者一括更新リクエスト"""

    assignee_id: int


class BulkPriorityUpdateRequest(BulkUpdateRequest):
    """優先度一括更新リクエスト"""

    priority_id: int


class BulkMilestoneUpdateRequest(BulkUpdateRequest):
    """マイルストーン一括更新リクエスト"""

    milestone_id: int


class BulkCategoryUpdateRequest(BulkUpdateRequest):
    """カテゴリ一括更新リクエスト"""

    category_id: int


def get_bulk_operations_service() -> BulkOperationsService:
    """
    一括操作サービスの依存性注入

    Returns:
        BulkOperationsService: 一括操作サービス
    """
    api_key = os.getenv("BACKLOG_API_KEY")
    space = os.getenv("BACKLOG_SPACE")

    if not api_key or not space:
        raise HTTPException(
            status_code=500,
            detail="Backlog API configuration is missing. Please set BACKLOG_API_KEY and BACKLOG_SPACE environment variables.",
        )

    backlog_client = BacklogClient(api_key=api_key, space=space, read_only_mode=settings.READ_ONLY_MODE)
    return BulkOperationsService(backlog_client=backlog_client)


@router.post(
    "/status", response_model=Dict[str, Any], operation_id="bulk_update_status"
)
async def bulk_update_status(
    request: BulkStatusUpdateRequest,
    bulk_service: BulkOperationsService = Depends(get_bulk_operations_service),
) -> Dict[str, Any]:
    """
    複数チケットのステータスを一括更新するエンドポイント

    Args:
        request: 一括更新リクエスト
        bulk_service: 一括操作サービス（依存性注入）

    Returns:
        処理結果の統計情報
    """
    try:
        result = bulk_service.bulk_update_status(
            issue_ids=request.issue_ids, status_id=request.status_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to bulk update status: {str(e)}"
        )


@router.post(
    "/assignee", response_model=Dict[str, Any], operation_id="bulk_update_assignee"
)
async def bulk_update_assignee(
    request: BulkAssigneeUpdateRequest,
    bulk_service: BulkOperationsService = Depends(get_bulk_operations_service),
) -> Dict[str, Any]:
    """
    複数チケットの担当者を一括更新するエンドポイント

    Args:
        request: 一括更新リクエスト
        bulk_service: 一括操作サービス（依存性注入）

    Returns:
        処理結果の統計情報
    """
    try:
        result = bulk_service.bulk_update_assignee(
            issue_ids=request.issue_ids, assignee_id=request.assignee_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to bulk update assignee: {str(e)}"
        )


@router.post(
    "/priority", response_model=Dict[str, Any], operation_id="bulk_update_priority"
)
async def bulk_update_priority(
    request: BulkPriorityUpdateRequest,
    bulk_service: BulkOperationsService = Depends(get_bulk_operations_service),
) -> Dict[str, Any]:
    """
    複数チケットの優先度を一括更新するエンドポイント

    Args:
        request: 一括更新リクエスト
        bulk_service: 一括操作サービス（依存性注入）

    Returns:
        処理結果の統計情報
    """
    try:
        result = bulk_service.bulk_update_priority(
            issue_ids=request.issue_ids, priority_id=request.priority_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to bulk update priority: {str(e)}"
        )


@router.post(
    "/milestone", response_model=Dict[str, Any], operation_id="bulk_update_milestone"
)
async def bulk_update_milestone(
    request: BulkMilestoneUpdateRequest,
    bulk_service: BulkOperationsService = Depends(get_bulk_operations_service),
) -> Dict[str, Any]:
    """
    複数チケットのマイルストーンを一括更新するエンドポイント

    Args:
        request: 一括更新リクエスト
        bulk_service: 一括操作サービス（依存性注入）

    Returns:
        処理結果の統計情報
    """
    try:
        result = bulk_service.bulk_update_milestone(
            issue_ids=request.issue_ids, milestone_id=request.milestone_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to bulk update milestone: {str(e)}"
        )


@router.post(
    "/category", response_model=Dict[str, Any], operation_id="bulk_update_category"
)
async def bulk_update_category(
    request: BulkCategoryUpdateRequest,
    bulk_service: BulkOperationsService = Depends(get_bulk_operations_service),
) -> Dict[str, Any]:
    """
    複数チケットのカテゴリを一括更新するエンドポイント

    Args:
        request: 一括更新リクエスト
        bulk_service: 一括操作サービス（依存性注入）

    Returns:
        処理結果の統計情報
    """
    try:
        result = bulk_service.bulk_update_category(
            issue_ids=request.issue_ids, category_id=request.category_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to bulk update category: {str(e)}"
        )


@router.post(
    "/delete", response_model=Dict[str, Any], operation_id="bulk_delete_issues"
)
async def bulk_delete_issues(
    request: BulkUpdateRequest,
    bulk_service: BulkOperationsService = Depends(get_bulk_operations_service),
) -> Dict[str, Any]:
    """
    複数チケットを一括削除するエンドポイント

    Args:
        request: 一括更新リクエスト
        bulk_service: 一括操作サービス（依存性注入）

    Returns:
        処理結果の統計情報
    """
    try:
        result = bulk_service.bulk_delete_issues(issue_ids=request.issue_ids)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to bulk delete issues: {str(e)}"
        )
