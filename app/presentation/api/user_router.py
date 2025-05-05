"""
ユーザー関連のAPIエンドポイント
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from app.infrastructure.backlog.backlog_client import BacklogClient
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# ルーターの作成
router = APIRouter(
    prefix="/api/users",
    tags=["users"],
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
            detail="Backlog API configuration is missing. Please set BACKLOG_API_KEY and BACKLOG_SPACE environment variables."
        )
    
    return BacklogClient(api_key=api_key, space=space)


@router.get("/", response_model=List[Dict[str, Any]], operation_id="get_users")
async def get_users(
    backlog_client: BacklogClient = Depends(get_backlog_client)
) -> List[Dict[str, Any]]:
    """
    ユーザー一覧を取得するエンドポイント
    
    Args:
        backlog_client: Backlogクライアント（依存性注入）
        
    Returns:
        ユーザー一覧
    """
    try:
        users = backlog_client.get_users()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get users: {str(e)}"
        )
