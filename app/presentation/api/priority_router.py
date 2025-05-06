"""
優先度関連のAPIエンドポイント
"""

import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException

from app.infrastructure.backlog.backlog_client import BacklogClient

# 環境変数の読み込み
load_dotenv()

# ルーターの作成
router = APIRouter(
    prefix="/api/priorities",
    tags=["priorities"],
    responses={404: {"description": "Not found"}},
)


def get_backlog_client() -> BacklogClient:
    """
    Backlogクライアントの依存性注入

    Returns:
        BacklogClient: Backlogクライアント
    """
    api_key = os.getenv("BACKLOG_API_KEY")
    space = os.getenv("BACKLOG_SPACE")

    if not api_key or not space:
        raise HTTPException(
            status_code=500,
            detail="Backlog API configuration is missing. Please set BACKLOG_API_KEY and BACKLOG_SPACE environment variables.",
        )

    return BacklogClient(api_key=api_key, space=space)


@router.get("/", response_model=List[Dict[str, Any]], operation_id="get_priorities")
async def get_priorities(
    backlog_client: BacklogClient = Depends(get_backlog_client),
) -> List[Dict[str, Any]]:
    """
    優先度一覧を取得するエンドポイント

    Args:
        backlog_client: Backlogクライアント（依存性注入）

    Returns:
        優先度一覧
    """
    try:
        priorities = backlog_client.get_priorities()
        return priorities
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get priorities: {str(e)}"
        )
