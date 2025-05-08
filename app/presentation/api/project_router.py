"""
プロジェクト関連のAPIエンドポイント
"""

import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException

from app.application.services.project_service import ProjectService
from app.infrastructure.backlog.backlog_client import BacklogClient # 正しくは backlog_client_wrapper を使うべき
from app.core.config import settings # settings をインポート

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
            detail="Backlog API configuration is missing. Please set BACKLOG_API_KEY and BACKLOG_SPACE environment variables.",
        )

    backlog_client = BacklogClient(api_key=api_key, space=space, read_only_mode=settings.READ_ONLY_MODE)
    return ProjectService(backlog_client=backlog_client)


@router.get("/", response_model=List[Dict[str, Any]], operation_id="get_projects")
async def get_projects(
    project_service: ProjectService = Depends(get_project_service),
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
        raise HTTPException(status_code=500, detail=f"Failed to get projects: {str(e)}")


@router.get("/{project_key}", response_model=Dict[str, Any], operation_id="get_project")
async def get_project(
    project_key: str, project_service: ProjectService = Depends(get_project_service)
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
                status_code=404, detail=f"Project with key {project_key} not found"
            )
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get project {project_key}: {str(e)}"
        )


@router.get(
    "/{project_key}/statuses",
    response_model=List[Dict[str, Any]],
    operation_id="get_project_statuses",
)
async def get_project_statuses(
    project_key: str, project_service: ProjectService = Depends(get_project_service)
) -> List[Dict[str, Any]]:
    """
    プロジェクトのステータス一覧を取得するエンドポイント

    Args:
        project_key: プロジェクトキー
        project_service: プロジェクト管理サービス（依存性注入）

    Returns:
        ステータス一覧
    """
    try:
        statuses = project_service.get_project_statuses(project_key)
        return statuses
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statuses for project {project_key}: {str(e)}",
        )


@router.get(
    "/{project_key}/issue-types",
    response_model=List[Dict[str, Any]],
    operation_id="get_project_issue_types",
)
async def get_project_issue_types(
    project_key: str, project_service: ProjectService = Depends(get_project_service)
) -> List[Dict[str, Any]]:
    """
    プロジェクトの課題種別一覧を取得するエンドポイント

    Args:
        project_key: プロジェクトキー
        project_service: プロジェクト管理サービス（依存性注入）

    Returns:
        課題種別一覧
    """
    try:
        issue_types = project_service.get_project_issue_types(project_key)
        return issue_types
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get issue types for project {project_key}: {str(e)}",
        )


@router.get(
    "/{project_key}/categories",
    response_model=List[Dict[str, Any]],
    operation_id="get_project_categories",
)
async def get_project_categories(
    project_key: str, project_service: ProjectService = Depends(get_project_service)
) -> List[Dict[str, Any]]:
    """
    プロジェクトのカテゴリー一覧を取得するエンドポイント

    Args:
        project_key: プロジェクトキー
        project_service: プロジェクト管理サービス（依存性注入）

    Returns:
        カテゴリー一覧
    """
    try:
        categories = project_service.get_project_categories(project_key)
        return categories
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get categories for project {project_key}: {str(e)}",
        )


@router.get(
    "/{project_key}/milestones",
    response_model=List[Dict[str, Any]],
    operation_id="get_project_milestones",
)
async def get_project_milestones(
    project_key: str, project_service: ProjectService = Depends(get_project_service)
) -> List[Dict[str, Any]]:
    """
    プロジェクトのマイルストーン一覧を取得するエンドポイント

    Args:
        project_key: プロジェクトキー
        project_service: プロジェクト管理サービス（依存性注入）

    Returns:
        マイルストーン一覧
    """
    try:
        milestones = project_service.get_project_milestones(project_key)
        return milestones
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get milestones for project {project_key}: {str(e)}",
        )


@router.get(
    "/{project_key}/versions",
    response_model=List[Dict[str, Any]],
    operation_id="get_project_versions",
)
async def get_project_versions(
    project_key: str, project_service: ProjectService = Depends(get_project_service)
) -> List[Dict[str, Any]]:
    """
    プロジェクトの発生バージョン一覧を取得するエンドポイント

    Args:
        project_key: プロジェクトキー
        project_service: プロジェクト管理サービス（依存性注入）

    Returns:
        発生バージョン一覧
    """
    try:
        versions = project_service.get_project_versions(project_key)
        return versions
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get versions for project {project_key}: {str(e)}",
        )
