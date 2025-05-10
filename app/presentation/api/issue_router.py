"""
課題関連のAPIエンドポイント
"""

import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Query
from app.infrastructure.backlog.backlog_client_wrapper import BacklogClientWrapper
from pydantic import BaseModel

from app.application.services.issue_service import IssueService
from app.infrastructure.backlog.backlog_client import BacklogClient # 正しくは backlog_client_wrapper を使うべきだが、既存コードに合わせる
from app.core.config import settings # settings をインポート

# 環境変数の読み込み
load_dotenv()

# ルーターの作成
router = APIRouter(
    prefix="/api/issues",
    tags=["issues"],
    responses={404: {"description": "Not found"}},
)


# リクエストボディのモデル
class IssueCreate(BaseModel):
    """課題作成リクエスト"""

    project_id: Optional[int] = None
    project_key: Optional[str] = None
    summary: str
    issue_type_id: Optional[int] = None
    issue_type_name: Optional[str] = None
    priority_id: Optional[int] = None
    priority_name: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    assignee_name: Optional[str] = None
    category_name: Optional[List[str]] = None
    milestone_name: Optional[List[str]] = None
    version_name: Optional[List[str]] = None
    start_date: Optional[str] = None
    due_date: Optional[str] = None


class IssueUpdate(BaseModel):
    """課題更新リクエスト"""

    summary: Optional[str] = None
    description: Optional[str] = None
    status_id: Optional[int] = None
    status_name: Optional[str] = None
    priority_id: Optional[int] = None
    priority_name: Optional[str] = None
    assignee_id: Optional[int] = None
    assignee_name: Optional[str] = None
    category_name: Optional[List[str]] = None
    milestone_name: Optional[List[str]] = None
    version_name: Optional[List[str]] = None
    start_date: Optional[str] = None
    due_date: Optional[str] = None


class CommentCreate(BaseModel):
    """コメント作成リクエスト"""

    content: str


def get_issue_service() -> IssueService:
    """
    課題管理サービスの依存性注入

    Returns:
        IssueService: 課題管理サービス
    """
    api_key = os.getenv("BACKLOG_API_KEY")
    space = os.getenv("BACKLOG_SPACE")

    if not api_key or not space:
        raise HTTPException(
            status_code=500,
            detail="Backlog API configuration is missing. Please set BACKLOG_API_KEY and BACKLOG_SPACE environment variables.",
        )

    backlog_client = BacklogClientWrapper(api_key=api_key, space=space, read_only_mode=settings.READ_ONLY_MODE)
    return IssueService(backlog_client=backlog_client)


@router.get("/", response_model=List[Dict[str, Any]], operation_id="get_issues")
async def get_issues(
    project_id: Optional[int] = None,
    keyword: Optional[str] = None,
    count: int = Query(20, ge=1, le=100),
    issue_service: IssueService = Depends(get_issue_service),
) -> List[Dict[str, Any]]:
    """
    課題一覧を取得するエンドポイント

    Args:
        project_id: プロジェクトID（指定しない場合は全プロジェクト）
        keyword: 検索キーワード
        count: 取得件数（1-100）
        issue_service: 課題管理サービス（依存性注入）

    Returns:
        課題一覧
    """
    try:
        issues = issue_service.get_issues(
            project_id=project_id, keyword=keyword, count=count
        )
        return issues
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get issues: {str(e)}")


@router.get(
    "/{issue_id_or_key}", response_model=Dict[str, Any], operation_id="get_issue"
)
async def get_issue(
    issue_id_or_key: str, issue_service: IssueService = Depends(get_issue_service)
) -> Dict[str, Any]:
    """
    課題情報を取得するエンドポイント

    Args:
        issue_id_or_key: 課題IDまたは課題キー
        issue_service: 課題管理サービス（依存性注入）

    Returns:
        課題情報
    """
    try:
        issue = issue_service.get_issue(issue_id_or_key)
        if issue is None:
            raise HTTPException(
                status_code=404,
                detail=f"Issue with ID or key {issue_id_or_key} not found",
            )
        return issue
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get issue {issue_id_or_key}: {str(e)}"
        )


@router.post(
    "/", response_model=Dict[str, Any], status_code=201, operation_id="create_issue"
)
async def create_issue(
    issue_data: IssueCreate, issue_service: IssueService = Depends(get_issue_service)
) -> Dict[str, Any]:
    """
    課題を作成するエンドポイント

    Args:
        issue_data: 課題作成データ
        issue_service: 課題管理サービス（依存性注入）

    Returns:
        作成された課題情報
    """
    try:
        # 名前ベースのパラメータを使用
        issue = issue_service.create_issue(
            project_id=issue_data.project_id,
            project_key=issue_data.project_key,
            summary=issue_data.summary,
            issue_type_id=issue_data.issue_type_id,
            issue_type_name=issue_data.issue_type_name,
            priority_id=issue_data.priority_id,
            priority_name=issue_data.priority_name,
            description=issue_data.description,
            assignee_id=issue_data.assignee_id,
            assignee_name=issue_data.assignee_name,
            category_name=issue_data.category_name,
            milestone_name=issue_data.milestone_name,
            version_name=issue_data.version_name,
            start_date=issue_data.start_date,
            due_date=issue_data.due_date,
        )
        return issue
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create issue: {str(e)}")


@router.patch(
    "/{issue_id_or_key}", response_model=Dict[str, Any], operation_id="update_issue"
)
async def update_issue(
    issue_id_or_key: str,
    issue_data: IssueUpdate,
    issue_service: IssueService = Depends(get_issue_service),
) -> Dict[str, Any]:
    """
    課題を更新するエンドポイント

    Args:
        issue_id_or_key: 課題IDまたは課題キー
        issue_data: 課題更新データ
        issue_service: 課題管理サービス（依存性注入）

    Returns:
        更新された課題情報
    """
    try:
        # 名前ベースのパラメータを使用
        issue = issue_service.update_issue(
            issue_id_or_key=issue_id_or_key,
            summary=issue_data.summary,
            description=issue_data.description,
            status_id=issue_data.status_id,
            status_name=issue_data.status_name,
            priority_id=issue_data.priority_id,
            priority_name=issue_data.priority_name,
            assignee_id=issue_data.assignee_id,
            assignee_name=issue_data.assignee_name,
            category_name=issue_data.category_name,
            milestone_name=issue_data.milestone_name,
            version_name=issue_data.version_name,
            start_date=issue_data.start_date,
            due_date=issue_data.due_date,
        )
        return issue
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update issue {issue_id_or_key}: {str(e)}",
        )


@router.delete("/{issue_id_or_key}", status_code=204, operation_id="delete_issue")
async def delete_issue(
    issue_id_or_key: str, issue_service: IssueService = Depends(get_issue_service)
) -> None:
    """
    課題を削除するエンドポイント

    Args:
        issue_id_or_key: 課題IDまたは課題キー
        issue_service: 課題管理サービス（依存性注入）
    """
    try:
        issue_service.delete_issue(issue_id_or_key)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete issue {issue_id_or_key}: {str(e)}",
        )


@router.post(
    "/{issue_id_or_key}/comments",
    response_model=Dict[str, Any],
    status_code=201,
    operation_id="add_comment",
)
async def add_comment(
    issue_id_or_key: str,
    comment_data: CommentCreate,
    issue_service: IssueService = Depends(get_issue_service),
) -> Dict[str, Any]:
    """
    課題にコメントを追加するエンドポイント

    Args:
        issue_id_or_key: 課題IDまたは課題キー
        comment_data: コメント作成データ
        issue_service: 課題管理サービス（依存性注入）

    Returns:
        追加されたコメント情報
    """
    try:
        comment = issue_service.add_comment(
            issue_id_or_key=issue_id_or_key, content=comment_data.content
        )
        return comment
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add comment to issue {issue_id_or_key}: {str(e)}",
        )


@router.get(
    "/{issue_id_or_key}/comments",
    response_model=List[Dict[str, Any]],
    operation_id="get_issue_comments",
)
async def get_issue_comments(
    issue_id_or_key: str,
    count: int = Query(20, ge=1, le=100),
    issue_service: IssueService = Depends(get_issue_service),
) -> List[Dict[str, Any]]:
    """
    課題のコメント一覧を取得するエンドポイント

    Args:
        issue_id_or_key: 課題IDまたは課題キー
        count: 取得件数（1-100）
        issue_service: 課題管理サービス（依存性注入）

    Returns:
        コメント一覧
    """
    try:
        comments = issue_service.get_issue_comments(
            issue_id_or_key=issue_id_or_key, count=count
        )
        return comments
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get comments for issue {issue_id_or_key}: {str(e)}",
        )
