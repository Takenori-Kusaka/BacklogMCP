"""
課題関連のMCPツール
"""
from typing import Dict, List, Any, Optional
from mcp.types import Tool
from app.application.services.issue_service import IssueService
from app.infrastructure.backlog.backlog_client import BacklogClient
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()


def get_issue_service() -> IssueService:
    """
    課題管理サービスのインスタンスを取得
    
    Returns:
        IssueService: 課題管理サービス
    """
    api_key = os.getenv("BACKLOG_API_KEY")
    space = os.getenv("BACKLOG_SPACE")
    
    if not api_key or not space:
        raise ValueError(
            "Backlog API configuration is missing. Please set BACKLOG_API_KEY and BACKLOG_SPACE environment variables."
        )
    
    backlog_client = BacklogClient(api_key=api_key, space=space)
    return IssueService(backlog_client=backlog_client)


# 課題一覧を取得するMCPツール
get_issues_tool = Tool(
    name="get_issues",
    description="Backlogの課題一覧を取得します",
    inputSchema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "プロジェクトID（指定しない場合は全プロジェクト）"
            },
            "keyword": {
                "type": "string",
                "description": "検索キーワード"
            },
            "count": {
                "type": "integer",
                "description": "取得件数（1-100）",
                "default": 20,
                "minimum": 1,
                "maximum": 100
            }
        }
    }
)

# @get_issues_tool.handler
async def get_issues_handler(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    課題一覧を取得するMCPツールのハンドラー
    
    Args:
        params: パラメータ
            - project_id: プロジェクトID（指定しない場合は全プロジェクト）
            - keyword: 検索キーワード
            - count: 取得件数（1-100）
        
    Returns:
        課題一覧
    """
    project_id = params.get("project_id")
    keyword = params.get("keyword")
    count = params.get("count", 20)
    
    issue_service = get_issue_service()
    return issue_service.get_issues(
        project_id=project_id,
        keyword=keyword,
        count=count
    )


# 課題情報を取得するMCPツール
get_issue_tool = Tool(
    name="get_issue",
    description="指定された課題の情報を取得します",
    inputSchema={
        "type": "object",
        "properties": {
            "issue_id_or_key": {
                "type": "string",
                "description": "課題IDまたは課題キー"
            }
        },
        "required": ["issue_id_or_key"]
    }
)

# @get_issue_tool.handler
async def get_issue_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    課題情報を取得するMCPツールのハンドラー
    
    Args:
        params: パラメータ
            - issue_id_or_key: 課題IDまたは課題キー
        
    Returns:
        課題情報
    """
    issue_id_or_key = params.get("issue_id_or_key")
    if not issue_id_or_key:
        raise ValueError("issue_id_or_key is required")
    
    issue_service = get_issue_service()
    issue = issue_service.get_issue(issue_id_or_key)
    
    if issue is None:
        raise ValueError(f"Issue with ID or key {issue_id_or_key} not found")
    
    return issue


# 課題を作成するMCPツール
create_issue_tool = Tool(
    name="create_issue",
    description="Backlogに新しい課題を作成します",
    inputSchema={
        "type": "object",
        "properties": {
            "project_id": {
                "type": "integer",
                "description": "プロジェクトID"
            },
            "project_key": {
                "type": "string",
                "description": "プロジェクトキー（project_idが指定されていない場合に使用）"
            },
            "summary": {
                "type": "string",
                "description": "課題の件名"
            },
            "issue_type_id": {
                "type": "integer",
                "description": "課題の種別ID"
            },
            "issue_type_name": {
                "type": "string",
                "description": "課題の種別名（issue_type_idが指定されていない場合に使用）"
            },
            "priority_id": {
                "type": "integer",
                "description": "優先度ID"
            },
            "priority_name": {
                "type": "string",
                "description": "優先度名（priority_idが指定されていない場合に使用）"
            },
            "description": {
                "type": "string",
                "description": "課題の詳細"
            },
            "assignee_id": {
                "type": "integer",
                "description": "担当者ID"
            },
            "assignee_name": {
                "type": "string",
                "description": "担当者名（assignee_idが指定されていない場合に使用）"
            },
            "category_name": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "カテゴリー名のリスト"
            },
            "milestone_name": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "マイルストーン名のリスト"
            },
            "version_name": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "発生バージョン名のリスト"
            },
            "start_date": {
                "type": "string",
                "description": "開始日（yyyy-MM-dd形式）"
            },
            "due_date": {
                "type": "string",
                "description": "期限日（yyyy-MM-dd形式）"
            }
        },
        "required": ["summary"]
    }
)

# @create_issue_tool.handler
async def create_issue_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    課題を作成するMCPツールのハンドラー
    
    Args:
        params: パラメータ
            - project_id: プロジェクトID
            - project_key: プロジェクトキー（project_idが指定されていない場合に使用）
            - summary: 課題の件名
            - issue_type_id: 課題の種別ID
            - issue_type_name: 課題の種別名（issue_type_idが指定されていない場合に使用）
            - priority_id: 優先度ID
            - priority_name: 優先度名（priority_idが指定されていない場合に使用）
            - description: 課題の詳細
            - assignee_id: 担当者ID
            - assignee_name: 担当者名（assignee_idが指定されていない場合に使用）
            - category_name: カテゴリー名のリスト
            - milestone_name: マイルストーン名のリスト
            - version_name: 発生バージョン名のリスト
            - start_date: 開始日（yyyy-MM-dd形式）
            - due_date: 期限日（yyyy-MM-dd形式）
        
    Returns:
        作成された課題情報
    """
    project_id = params.get("project_id")
    project_key = params.get("project_key")
    summary = params.get("summary")
    issue_type_id = params.get("issue_type_id")
    issue_type_name = params.get("issue_type_name")
    priority_id = params.get("priority_id")
    priority_name = params.get("priority_name")
    description = params.get("description")
    assignee_id = params.get("assignee_id")
    assignee_name = params.get("assignee_name")
    category_name = params.get("category_name")
    milestone_name = params.get("milestone_name")
    version_name = params.get("version_name")
    start_date = params.get("start_date")
    due_date = params.get("due_date")
    
    if not summary or (not project_id and not project_key):
        raise ValueError("summary and either project_id or project_key are required")
    
    issue_service = get_issue_service()
    return issue_service.create_issue(
        project_id=project_id,
        project_key=project_key,
        summary=summary,
        issue_type_id=issue_type_id,
        issue_type_name=issue_type_name,
        priority_id=priority_id,
        priority_name=priority_name,
        description=description,
        assignee_id=assignee_id,
        assignee_name=assignee_name,
        category_name=category_name,
        milestone_name=milestone_name,
        version_name=version_name,
        start_date=start_date,
        due_date=due_date
    )


# 課題を更新するMCPツール
update_issue_tool = Tool(
    name="update_issue",
    description="指定された課題の情報を更新します",
    inputSchema={
        "type": "object",
        "properties": {
            "issue_id_or_key": {
                "type": "string",
                "description": "課題IDまたは課題キー"
            },
            "summary": {
                "type": "string",
                "description": "課題の件名"
            },
            "description": {
                "type": "string",
                "description": "課題の詳細"
            },
            "status_id": {
                "type": "integer",
                "description": "ステータスID"
            },
            "status_name": {
                "type": "string",
                "description": "ステータス名（status_idが指定されていない場合に使用）"
            },
            "priority_id": {
                "type": "integer",
                "description": "優先度ID"
            },
            "priority_name": {
                "type": "string",
                "description": "優先度名（priority_idが指定されていない場合に使用）"
            },
            "assignee_id": {
                "type": "integer",
                "description": "担当者ID"
            },
            "assignee_name": {
                "type": "string",
                "description": "担当者名（assignee_idが指定されていない場合に使用）"
            },
            "category_name": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "カテゴリー名のリスト"
            },
            "milestone_name": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "マイルストーン名のリスト"
            },
            "version_name": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "発生バージョン名のリスト"
            },
            "start_date": {
                "type": "string",
                "description": "開始日（yyyy-MM-dd形式）"
            },
            "due_date": {
                "type": "string",
                "description": "期限日（yyyy-MM-dd形式）"
            }
        },
        "required": ["issue_id_or_key"]
    }
)

# @update_issue_tool.handler
async def update_issue_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    課題を更新するMCPツールのハンドラー
    
    Args:
        params: パラメータ
            - issue_id_or_key: 課題IDまたは課題キー
            - summary: 課題の件名
            - description: 課題の詳細
            - status_id: ステータスID
            - status_name: ステータス名（status_idが指定されていない場合に使用）
            - priority_id: 優先度ID
            - priority_name: 優先度名（priority_idが指定されていない場合に使用）
            - assignee_id: 担当者ID
            - assignee_name: 担当者名（assignee_idが指定されていない場合に使用）
            - category_name: カテゴリー名のリスト
            - milestone_name: マイルストーン名のリスト
            - version_name: 発生バージョン名のリスト
            - start_date: 開始日（yyyy-MM-dd形式）
            - due_date: 期限日（yyyy-MM-dd形式）
        
    Returns:
        更新された課題情報
    """
    issue_id_or_key = params.get("issue_id_or_key")
    if not issue_id_or_key:
        raise ValueError("issue_id_or_key is required")
    
    summary = params.get("summary")
    description = params.get("description")
    status_id = params.get("status_id")
    status_name = params.get("status_name")
    priority_id = params.get("priority_id")
    priority_name = params.get("priority_name")
    assignee_id = params.get("assignee_id")
    assignee_name = params.get("assignee_name")
    category_name = params.get("category_name")
    milestone_name = params.get("milestone_name")
    version_name = params.get("version_name")
    start_date = params.get("start_date")
    due_date = params.get("due_date")
    
    issue_service = get_issue_service()
    return issue_service.update_issue(
        issue_id_or_key=issue_id_or_key,
        summary=summary,
        description=description,
        status_id=status_id,
        status_name=status_name,
        priority_id=priority_id,
        priority_name=priority_name,
        assignee_id=assignee_id,
        assignee_name=assignee_name,
        category_name=category_name,
        milestone_name=milestone_name,
        version_name=version_name,
        start_date=start_date,
        due_date=due_date
    )


# 課題を削除するMCPツール
delete_issue_tool = Tool(
    name="delete_issue",
    description="指定された課題を削除します",
    inputSchema={
        "type": "object",
        "properties": {
            "issue_id_or_key": {
                "type": "string",
                "description": "課題IDまたは課題キー"
            }
        },
        "required": ["issue_id_or_key"]
    }
)

# @delete_issue_tool.handler
async def delete_issue_handler(params: Dict[str, Any]) -> bool:
    """
    課題を削除するMCPツールのハンドラー
    
    Args:
        params: パラメータ
            - issue_id_or_key: 課題IDまたは課題キー
        
    Returns:
        削除に成功した場合はTrue
    """
    issue_id_or_key = params.get("issue_id_or_key")
    if not issue_id_or_key:
        raise ValueError("issue_id_or_key is required")
    
    issue_service = get_issue_service()
    return issue_service.delete_issue(issue_id_or_key)


# 課題にコメントを追加するMCPツール
add_comment_tool = Tool(
    name="add_comment",
    description="指定された課題にコメントを追加します",
    inputSchema={
        "type": "object",
        "properties": {
            "issue_id_or_key": {
                "type": "string",
                "description": "課題IDまたは課題キー"
            },
            "content": {
                "type": "string",
                "description": "コメント内容"
            }
        },
        "required": ["issue_id_or_key", "content"]
    }
)

# @add_comment_tool.handler
async def add_comment_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    課題にコメントを追加するMCPツールのハンドラー
    
    Args:
        params: パラメータ
            - issue_id_or_key: 課題IDまたは課題キー
            - content: コメント内容
        
    Returns:
        追加されたコメント情報
    """
    issue_id_or_key = params.get("issue_id_or_key")
    content = params.get("content")
    
    if not issue_id_or_key or not content:
        raise ValueError("issue_id_or_key and content are required")
    
    issue_service = get_issue_service()
    return issue_service.add_comment(
        issue_id_or_key=issue_id_or_key,
        content=content
    )


# 課題のコメント一覧を取得するMCPツール
get_issue_comments_tool = Tool(
    name="get_issue_comments",
    description="指定された課題のコメント一覧を取得します",
    inputSchema={
        "type": "object",
        "properties": {
            "issue_id_or_key": {
                "type": "string",
                "description": "課題IDまたは課題キー"
            },
            "count": {
                "type": "integer",
                "description": "取得件数（1-100）",
                "default": 20,
                "minimum": 1,
                "maximum": 100
            }
        },
        "required": ["issue_id_or_key"]
    }
)

# @get_issue_comments_tool.handler
async def get_issue_comments_handler(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    課題のコメント一覧を取得するMCPツールのハンドラー
    
    Args:
        params: パラメータ
            - issue_id_or_key: 課題IDまたは課題キー
            - count: 取得件数（1-100）
        
    Returns:
        コメント一覧
    """
    issue_id_or_key = params.get("issue_id_or_key")
    count = params.get("count", 20)
    
    if not issue_id_or_key:
        raise ValueError("issue_id_or_key is required")
    
    issue_service = get_issue_service()
    return issue_service.get_issue_comments(
        issue_id_or_key=issue_id_or_key,
        count=count
    )


# 課題種別一覧を取得するMCPツール
get_issue_types_tool = Tool(
    name="get_issue_types",
    description="指定されたプロジェクトの課題種別一覧を取得します",
    inputSchema={
        "type": "object",
        "properties": {
            "project_key": {
                "type": "string",
                "description": "プロジェクトキー"
            }
        },
        "required": ["project_key"]
    }
)

# @get_issue_types_tool.handler
async def get_issue_types_handler(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    課題種別一覧を取得するMCPツールのハンドラー
    
    Args:
        params: パラメータ
            - project_key: プロジェクトキー
        
    Returns:
        課題種別一覧
    """
    project_key = params.get("project_key")
    
    if not project_key:
        raise ValueError("project_key is required")
    
    issue_service = get_issue_service()
    return issue_service.get_issue_types(project_key)


# 課題一覧リソース
issues_resource = {
    "uri": "issues",
    "name": "Backlogの課題一覧",
    "description": "Backlogの課題一覧を取得するリソース"
}

# @issues_resource.handler
async def issues_resource_handler() -> List[Dict[str, Any]]:
    """
    課題一覧リソースのハンドラー
    
    Returns:
        課題一覧
    """
    issue_service = get_issue_service()
    return issue_service.get_issues()
