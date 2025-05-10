"""
プロジェクト関連のMCPツール
"""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp.types import Tool

from app.application.services.project_service import ProjectService
from app.infrastructure.backlog.backlog_client_wrapper import BacklogClientWrapper
from app.core.config import settings

# 環境変数の読み込み
load_dotenv()


def get_project_service() -> ProjectService:
    """
    プロジェクト管理サービスのインスタンスを取得

    Returns:
        ProjectService: プロジェクト管理サービス
    """
    api_key = os.getenv("BACKLOG_API_KEY")
    space = os.getenv("BACKLOG_SPACE")

    if not api_key or not space:
        raise ValueError(
            "Backlog API configuration is missing. Please set BACKLOG_API_KEY and BACKLOG_SPACE environment variables."
        )

    backlog_client = BacklogClientWrapper(api_key=api_key, space=space, read_only_mode=settings.READ_ONLY_MODE)
    return ProjectService(backlog_client=backlog_client)


# プロジェクト一覧を取得するMCPツール
get_projects_tool = Tool(
    name="get_projects",
    description="Backlogのプロジェクト一覧を取得します",
    inputSchema={"type": "object", "properties": {}, "required": []},
)


# @get_projects_tool.handler
async def get_projects_handler(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    プロジェクト一覧を取得するMCPツールのハンドラー

    Args:
        params: パラメータ（このツールでは使用しない）

    Returns:
        プロジェクト一覧
    """
    project_service = get_project_service()
    return project_service.get_projects()


# 特定のプロジェクトを取得するMCPツール
get_project_tool = Tool(
    name="get_project",
    description="指定されたプロジェクトキーのプロジェクト情報を取得します",
    inputSchema={
        "type": "object",
        "properties": {
            "project_key": {"type": "string", "description": "プロジェクトキー"}
        },
        "required": ["project_key"],
    },
)


# @get_project_tool.handler
async def get_project_handler(params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    特定のプロジェクトを取得するMCPツールのハンドラー

    Args:
        params: パラメータ
            - project_key: プロジェクトキー

    Returns:
        プロジェクト情報
    """
    project_key = params.get("project_key")
    if not project_key:
        raise ValueError("project_key is required")

    project_service = get_project_service()
    project = project_service.get_project(project_key)

    if project is None:
        raise ValueError(f"Project with key {project_key} not found")

    return project


# プロジェクト一覧リソース
projects_resource = {
    "uri": "projects",
    "name": "Backlogのプロジェクト一覧",
    "description": "Backlogのプロジェクト一覧を取得するリソース",
}


# @projects_resource.handler
async def projects_resource_handler() -> List[Dict[str, Any]]:
    """
    プロジェクト一覧リソースのハンドラー

    Returns:
        プロジェクト一覧
    """
    project_service = get_project_service()
    return project_service.get_projects()
