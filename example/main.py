"""
Backlog API サンプルアプリケーション

このサンプルアプリケーションは、BacklogMCPプロジェクトのAPIを使用して
Backlogの課題を操作する方法を示します。
"""
import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# BacklogMCPのクライアントをインポート
from app.infrastructure.backlog.backlog_client import BacklogClient

app = FastAPI(
    title="Backlog API サンプルアプリケーション",
    description="BacklogMCPプロジェクトを使用したBacklog API操作のサンプル",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 環境変数からBacklog APIの設定を取得
BACKLOG_API_KEY = os.getenv("BACKLOG_API_KEY", "")
BACKLOG_SPACE = os.getenv("BACKLOG_SPACE", "")
BACKLOG_PROJECT = os.getenv("BACKLOG_PROJECT", "")

# BacklogClientのインスタンスを取得する関数
def get_backlog_client():
    if not BACKLOG_API_KEY or not BACKLOG_SPACE:
        raise HTTPException(
            status_code=500,
            detail="Backlog API設定が不足しています。BACKLOG_API_KEYとBACKLOG_SPACEを設定してください。"
        )
    return BacklogClient(api_key=BACKLOG_API_KEY, space=BACKLOG_SPACE)

# モデル定義
class IssueCreate(BaseModel):
    project_key: str
    summary: str
    description: Optional[str] = None
    issue_type_name: Optional[str] = None
    priority_name: Optional[str] = None
    assignee_name: Optional[str] = None
    status_name: Optional[str] = None
    category_name: Optional[List[str]] = None
    milestone_name: Optional[List[str]] = None
    version_name: Optional[List[str]] = None
    start_date: Optional[str] = None
    due_date: Optional[str] = None

class IssueUpdate(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    issue_type_name: Optional[str] = None
    priority_name: Optional[str] = None
    assignee_name: Optional[str] = None
    status_name: Optional[str] = None
    category_name: Optional[List[str]] = None
    milestone_name: Optional[List[str]] = None
    version_name: Optional[List[str]] = None
    start_date: Optional[str] = None
    due_date: Optional[str] = None

class CommentCreate(BaseModel):
    content: str

# ルート定義
@app.get("/")
def read_root():
    return {
        "message": "Backlog API サンプルアプリケーション",
        "endpoints": [
            {"path": "/projects", "description": "プロジェクト一覧を取得"},
            {"path": "/projects/{project_key}", "description": "プロジェクト詳細を取得"},
            {"path": "/issues", "description": "課題一覧を取得"},
            {"path": "/issues/{issue_id_or_key}", "description": "課題詳細を取得"},
            {"path": "/issues", "method": "POST", "description": "課題を作成"},
            {"path": "/issues/{issue_id_or_key}", "method": "PUT", "description": "課題を更新"},
            {"path": "/issues/{issue_id_or_key}/comments", "method": "POST", "description": "コメントを追加"},
            {"path": "/users", "description": "ユーザー一覧を取得"},
            {"path": "/priorities", "description": "優先度一覧を取得"},
            {"path": "/projects/{project_key}/statuses", "description": "ステータス一覧を取得"},
            {"path": "/projects/{project_key}/categories", "description": "カテゴリー一覧を取得"},
            {"path": "/projects/{project_key}/milestones", "description": "マイルストーン一覧を取得"},
            {"path": "/projects/{project_key}/versions", "description": "バージョン一覧を取得"},
        ]
    }

# プロジェクト関連のエンドポイント
@app.get("/projects")
def get_projects(client: BacklogClient = Depends(get_backlog_client)):
    """プロジェクト一覧を取得"""
    return client.get_projects()

@app.get("/projects/{project_key}")
def get_project(project_key: str, client: BacklogClient = Depends(get_backlog_client)):
    """プロジェクト詳細を取得"""
    project = client.get_project(project_key)
    if not project:
        raise HTTPException(status_code=404, detail=f"プロジェクト '{project_key}' が見つかりません")
    return project

# 課題関連のエンドポイント
@app.get("/issues")
def get_issues(
    project_id: Optional[int] = None,
    status_id: Optional[List[int]] = Query(None),
    assignee_id: Optional[int] = None,
    keyword: Optional[str] = None,
    count: int = 20,
    client: BacklogClient = Depends(get_backlog_client)
):
    """課題一覧を取得"""
    return client.get_issues(
        project_id=project_id,
        status_id=status_id,
        assignee_id=assignee_id,
        keyword=keyword,
        count=count
    )

@app.get("/issues/{issue_id_or_key}")
def get_issue(issue_id_or_key: str, client: BacklogClient = Depends(get_backlog_client)):
    """課題詳細を取得"""
    issue = client.get_issue(issue_id_or_key)
    if not issue:
        raise HTTPException(status_code=404, detail=f"課題 '{issue_id_or_key}' が見つかりません")
    return issue

@app.post("/issues", status_code=201)
def create_issue(issue: IssueCreate, client: BacklogClient = Depends(get_backlog_client)):
    """課題を作成（名前ベースのパラメータを使用）"""
    result = client.create_issue(
        project_key=issue.project_key,
        summary=issue.summary,
        description=issue.description,
        issue_type_name=issue.issue_type_name,
        priority_name=issue.priority_name,
        assignee_name=issue.assignee_name,
        category_name=issue.category_name,
        milestone_name=issue.milestone_name,
        version_name=issue.version_name,
        start_date=issue.start_date,
        due_date=issue.due_date
    )
    
    if not result:
        raise HTTPException(status_code=500, detail="課題の作成に失敗しました")
    return result

@app.put("/issues/{issue_id_or_key}")
def update_issue(
    issue_id_or_key: str,
    issue: IssueUpdate,
    client: BacklogClient = Depends(get_backlog_client)
):
    """課題を更新（名前ベースのパラメータを使用）"""
    result = client.update_issue(
        issue_id_or_key=issue_id_or_key,
        summary=issue.summary,
        description=issue.description,
        status_name=issue.status_name,
        priority_name=issue.priority_name,
        assignee_name=issue.assignee_name,
        category_name=issue.category_name,
        milestone_name=issue.milestone_name,
        version_name=issue.version_name,
        start_date=issue.start_date,
        due_date=issue.due_date
    )
    
    if not result:
        raise HTTPException(status_code=500, detail=f"課題 '{issue_id_or_key}' の更新に失敗しました")
    return result

@app.post("/issues/{issue_id_or_key}/comments", status_code=201)
def add_comment(
    issue_id_or_key: str,
    comment: CommentCreate,
    client: BacklogClient = Depends(get_backlog_client)
):
    """課題にコメントを追加"""
    result = client.add_comment(
        issue_id_or_key=issue_id_or_key,
        content=comment.content
    )
    
    if not result:
        raise HTTPException(status_code=500, detail=f"課題 '{issue_id_or_key}' へのコメント追加に失敗しました")
    return result

@app.get("/issues/{issue_id_or_key}/comments")
def get_comments(
    issue_id_or_key: str,
    count: int = 20,
    client: BacklogClient = Depends(get_backlog_client)
):
    """課題のコメント一覧を取得"""
    return client.get_issue_comments(
        issue_id_or_key=issue_id_or_key,
        count=count
    )

# マスターデータ取得用のエンドポイント
@app.get("/users")
def get_users(client: BacklogClient = Depends(get_backlog_client)):
    """ユーザー一覧を取得"""
    return client.get_users()

@app.get("/priorities")
def get_priorities(client: BacklogClient = Depends(get_backlog_client)):
    """優先度一覧を取得"""
    return client.get_priorities()

@app.get("/projects/{project_key}/statuses")
def get_statuses(project_key: str, client: BacklogClient = Depends(get_backlog_client)):
    """ステータス一覧を取得"""
    return client.get_statuses(project_key)

@app.get("/projects/{project_key}/categories")
def get_categories(project_key: str, client: BacklogClient = Depends(get_backlog_client)):
    """カテゴリー一覧を取得"""
    return client.get_categories(project_key)

@app.get("/projects/{project_key}/milestones")
def get_milestones(project_key: str, client: BacklogClient = Depends(get_backlog_client)):
    """マイルストーン一覧を取得"""
    return client.get_milestones(project_key)

@app.get("/projects/{project_key}/versions")
def get_versions(project_key: str, client: BacklogClient = Depends(get_backlog_client)):
    """バージョン一覧を取得"""
    return client.get_versions(project_key)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
