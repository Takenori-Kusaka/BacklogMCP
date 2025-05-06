"""
モックデータ
"""

from typing import Any, Dict, List

# プロジェクト一覧のモックデータ
MOCK_PROJECTS = [
    {
        "id": 1,
        "projectKey": "TEST",
        "name": "テストプロジェクト",
        "chartEnabled": False,
        "subtaskingEnabled": False,
        "projectLeaderCanEditProjectLeader": False,
        "useWikiTreeView": False,
        "textFormattingRule": "markdown",
        "archived": False,
    }
]

# ユーザー一覧のモックデータ
MOCK_USERS = [
    {
        "id": 1,
        "userId": "admin",
        "name": "管理者",
        "roleType": 1,
        "lang": "ja",
        "mailAddress": "admin@example.com",
    },
    {
        "id": 2,
        "userId": "user",
        "name": "一般ユーザー",
        "roleType": 2,
        "lang": "ja",
        "mailAddress": "user@example.com",
    },
]

# 優先度一覧のモックデータ
MOCK_PRIORITIES = [
    {"id": 2, "name": "高"},
    {"id": 3, "name": "中"},
    {"id": 4, "name": "低"},
]

# ステータス一覧のモックデータ
MOCK_STATUSES = [
    {"id": 1, "name": "未対応"},
    {"id": 2, "name": "処理中"},
    {"id": 3, "name": "処理済み"},
    {"id": 4, "name": "完了"},
]

# 課題種別一覧のモックデータ
MOCK_ISSUE_TYPES = [
    {"id": 1, "projectId": 1, "name": "タスク", "color": "#7ea800"},
    {"id": 2, "projectId": 1, "name": "バグ", "color": "#990000"},
    {"id": 3, "projectId": 1, "name": "要望", "color": "#ff9200"},
]

# カテゴリー一覧のモックデータ
MOCK_CATEGORIES = [
    {"id": 1, "name": "フロントエンド", "displayOrder": 0},
    {"id": 2, "name": "バックエンド", "displayOrder": 1},
    {"id": 3, "name": "インフラ", "displayOrder": 2},
]

# マイルストーン一覧のモックデータ
MOCK_MILESTONES = [
    {
        "id": 1,
        "projectId": 1,
        "name": "v1.0.0",
        "description": "初回リリース",
        "startDate": "2025-01-01",
        "releaseDueDate": "2025-03-31",
        "archived": False,
    },
    {
        "id": 2,
        "projectId": 1,
        "name": "v1.1.0",
        "description": "機能追加",
        "startDate": "2025-04-01",
        "releaseDueDate": "2025-06-30",
        "archived": False,
    },
]

# 課題一覧のモックデータ
MOCK_ISSUES = [
    {
        "id": 1,
        "projectId": 1,
        "issueKey": "TEST-1",
        "keyId": 1,
        "issueType": {"id": 1, "projectId": 1, "name": "タスク", "color": "#7ea800"},
        "summary": "サンプル課題1",
        "description": "サンプル課題1の詳細",
        "status": {"id": 1, "name": "未対応"},
        "priority": {"id": 3, "name": "中"},
        "assignee": {
            "id": 1,
            "userId": "admin",
            "name": "管理者",
            "roleType": 1,
            "lang": "ja",
            "mailAddress": "admin@example.com",
        },
        "startDate": None,
        "dueDate": None,
        "estimatedHours": None,
        "actualHours": None,
        "parentIssueId": None,
        "createdUser": {
            "id": 1,
            "userId": "admin",
            "name": "管理者",
            "roleType": 1,
            "lang": "ja",
            "mailAddress": "admin@example.com",
        },
        "created": "2025-01-01T00:00:00Z",
        "updatedUser": {
            "id": 1,
            "userId": "admin",
            "name": "管理者",
            "roleType": 1,
            "lang": "ja",
            "mailAddress": "admin@example.com",
        },
        "updated": "2025-01-01T00:00:00Z",
    }
]

# コメント一覧のモックデータ
MOCK_COMMENTS = [
    {
        "id": 1,
        "content": "サンプルコメント1",
        "changeLog": [],
        "createdUser": {
            "id": 1,
            "userId": "admin",
            "name": "管理者",
            "roleType": 1,
            "lang": "ja",
            "mailAddress": "admin@example.com",
        },
        "created": "2025-01-01T00:00:00Z",
        "updated": "2025-01-01T00:00:00Z",
        "stars": [],
        "notifications": [],
    }
]
