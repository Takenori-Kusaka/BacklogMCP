"""
プロジェクト関連のAPIエンドポイント
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from app.application.services.project_service import ProjectService
from app.infrastructure.backlog.backlog_client import BacklogClient
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# ルーターの作成
router = APIRouter(
    prefix="/api/projects",
    tags=["projects"],
    responses={404: {"description": "Not found"}},
)


def get_project_service() -> ProjectService:
    """
    プロジェクト管理サービスの依存性注入
    
    Returns:
        ProjectService: プロジェクト管理サービス
    """
    api_key = os.getenv("BACKLOG_API_KEY")
    space = os.getenv("BACKLOG_SPACE")
    
    if not api_key or not space:
        raise HTTPException(
            status_code=500,
            detail="Backlog API configuration is missing. Please set BACKLOG_API_KEY and BACKLOG_SPACE environment variables."
        )
    
    backlog_client = BacklogClient(api_key=api_key, space=space)
    return ProjectService(backlog_client=backlog_client)


@router.get("/", response_model=List[Dict[str, Any]])
async def get_projects(
    project_service: ProjectService = Depends(get_project_service)
) -> List[Dict[str, Any]]:
    """
    プロジェクト一覧を取得するエンドポイント
    
    Args:
        project_service: プロジェクト管理サービス（依存性注入）
        
    Returns:
        プロジェクト一覧
    """
    try:
        projects = project_service.get_projects()
        return projects
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get projects: {str(e)}"
        )


@router.get("/{project_key}", response_model=Dict[str, Any])
async def get_project(
    project_key: str,
    project_service: ProjectService = Depends(get_project_service)
) -> Dict[str, Any]:
    """
    プロジェクトを取得するエンドポイント
    
    Args:
        project_key: プロジェクトキー
        project_service: プロジェクト管理サービス（依存性注入）
        
    Returns:
        プロジェクト情報
    """
    try:
        project = project_service.get_project(project_key)
        if project is None:
            raise HTTPException(
                status_code=404,
                detail=f"Project with key {project_key} not found"
            )
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get project {project_key}: {str(e)}"
        )
