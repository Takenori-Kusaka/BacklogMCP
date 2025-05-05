"""
Backlog APIクライアント
"""
from typing import Dict, List, Optional, Any, Union
import os
import json
from pybacklogpy.BacklogConfigure import BacklogComConfigure
import urllib3
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# テスト環境でのみ使用する場合は、SSL証明書の検証を無効化
# 注意: 本番環境では使用しないでください
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# requestsのデフォルト設定を変更（テスト環境でのみ使用）
old_request = requests.request
def new_request(*args, **kwargs):
    kwargs['verify'] = False
    return old_request(*args, **kwargs)
requests.request = new_request
from pybacklogpy.Project import Project
from pybacklogpy.Issue import Issue, IssueComment, IssueType
from pybacklogpy.User import User
from pybacklogpy.Status import Status
from pybacklogpy.Priority import Priority
from pybacklogpy.Category import Category
from pybacklogpy.Version import Version


class BacklogClient:
    """
    Backlog APIクライアント
    
    PyBacklogPyを使用してBacklog APIと通信するクライアントクラス
    """
    
    def __init__(self, api_key: str, space: str):
        """
        初期化
        
        Args:
            api_key: Backlog APIキー
            space: Backlogスペース名
        """
        self.config = BacklogComConfigure(space, api_key)
        self.project_api = Project(self.config)
        self.issue_api = Issue(self.config)
        self.issue_comment_api = IssueComment(self.config)
        self.issue_type_api = IssueType(self.config)
        self.user_api = User(self.config)
        self.status_api = Status(self.config)
        self.priority_api = Priority(self.config)
        self.category_api = Category(self.config)
        self.milestone_api = Version(self.config)
        self.version_api = Version(self.config)
        
        # キャッシュ
        self._users_cache = None
        self._priorities_cache = None
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """
        プロジェクト一覧を取得
        
        Returns:
            プロジェクト一覧
        """
        response = self.project_api.get_project_list()
        return json.loads(response.text)
    
    def get_project(self, project_key: str) -> Optional[Dict[str, Any]]:
        """
        プロジェクトを取得
        
        Args:
            project_key: プロジェクトキー
            
        Returns:
            プロジェクト情報。プロジェクトが存在しない場合はNone
        """
        try:
            response = self.project_api.get_project(project_key)
            return json.loads(response.text)
        except Exception as e:
            # プロジェクトが存在しない場合などのエラー処理
            print(f"Error getting project {project_key}: {e}")
            return None
    
    def get_issues(self, project_id: Optional[int] = None, status_id: Optional[List[int]] = None, 
                  assignee_id: Optional[int] = None, keyword: Optional[str] = None, 
                  count: int = 20) -> List[Dict[str, Any]]:
        """
        課題一覧を取得
        
        Args:
            project_id: プロジェクトID（指定しない場合は全プロジェクト）
            status_id: ステータスID（指定しない場合は全ステータス）
            assignee_id: 担当者ID（指定しない場合は全担当者）
            keyword: 検索キーワード
            count: 取得件数（デフォルト20件）
            
        Returns:
            課題一覧
        """
        try:
            project_id_list = [project_id] if project_id else None
            status_id_list = status_id if status_id else None
            assignee_id_list = [assignee_id] if assignee_id else None
            
            response = self.issue_api.get_issue_list(
                project_id=project_id_list,
                status_id=status_id_list,
                assignee_id=assignee_id_list,
                keyword=keyword,
                count=count
            )
            
            return json.loads(response.text)
        except Exception as e:
            print(f"Error getting issues: {e}")
            return []
    
    def get_issue(self, issue_id_or_key: str) -> Optional[Dict[str, Any]]:
        """
        課題情報を取得
        
        Args:
            issue_id_or_key: 課題IDまたは課題キー
            
        Returns:
            課題情報。課題が存在しない場合はNone
        """
        try:
            response = self.issue_api.get_issue(issue_id_or_key)
            return json.loads(response.text)
        except Exception as e:
            print(f"Error getting issue {issue_id_or_key}: {e}")
            return None
    
    def get_users(self) -> List[Dict[str, Any]]:
        """
        ユーザー一覧を取得
        
        Returns:
            ユーザー一覧
        """
        if self._users_cache is None:
            try:
                response = self.user_api.get_user_list()
                self._users_cache = json.loads(response.text)
            except Exception as e:
                print(f"Error getting users: {e}")
                self._users_cache = []
        return self._users_cache
    
    def get_user_id_by_name(self, user_name: str) -> Optional[int]:
        """
        ユーザー名からユーザーIDを取得
        
        Args:
            user_name: ユーザー名
            
        Returns:
            ユーザーID。ユーザーが存在しない場合はNone
        """
        users = self.get_users()
        for user in users:
            if user.get("name") == user_name:
                return user.get("id")
        return None
    
    def get_priorities(self) -> List[Dict[str, Any]]:
        """
        優先度一覧を取得
        
        Returns:
            優先度一覧
        """
        if self._priorities_cache is None:
            try:
                response = self.priority_api.get_priority_list()
                self._priorities_cache = json.loads(response.text)
            except Exception as e:
                print(f"Error getting priorities: {e}")
                self._priorities_cache = []
        return self._priorities_cache
    
    def get_priority_id_by_name(self, priority_name: str) -> Optional[int]:
        """
        優先度名から優先度IDを取得
        
        Args:
            priority_name: 優先度名
            
        Returns:
            優先度ID。優先度が存在しない場合はNone
        """
        priorities = self.get_priorities()
        for priority in priorities:
            if priority.get("name") == priority_name:
                return priority.get("id")
        return None
    
    def get_statuses(self, project_id_or_key: str) -> List[Dict[str, Any]]:
        """
        ステータス一覧を取得
        
        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー
            
        Returns:
            ステータス一覧
        """
        try:
            # PyBacklogPyのバージョンによっては、get_status_listメソッドがない場合があるため、
            # 代わりにget_status_list_of_projectメソッドを使用
            if hasattr(self.status_api, 'get_status_list'):
                response = self.status_api.get_status_list(project_id_or_key)
            else:
                response = self.status_api.get_status_list_of_project(project_id_or_key)
            return json.loads(response.text)
        except Exception as e:
            print(f"Error getting statuses for project {project_id_or_key}: {e}")
            # エラーが発生した場合は、デフォルトのステータス一覧を返す
            return [
                {"id": 1, "name": "未対応"},
                {"id": 2, "name": "処理中"},
                {"id": 3, "name": "処理済み"},
                {"id": 4, "name": "完了"}
            ]
    
    def get_status_id_by_name(self, project_id_or_key: str, status_name: str) -> Optional[int]:
        """
        ステータス名からステータスIDを取得
        
        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー
            status_name: ステータス名
            
        Returns:
            ステータスID。ステータスが存在しない場合はNone
        """
        statuses = self.get_statuses(project_id_or_key)
        for status in statuses:
            if status.get("name") == status_name:
                return status.get("id")
        return None
    
    def get_categories(self, project_id_or_key: str) -> List[Dict[str, Any]]:
        """
        カテゴリー一覧を取得
        
        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー
            
        Returns:
            カテゴリー一覧
        """
        try:
            response = self.category_api.get_category_list(project_id_or_key)
            return json.loads(response.text)
        except Exception as e:
            print(f"Error getting categories for project {project_id_or_key}: {e}")
            return []
    
    def get_category_id_by_name(self, project_id_or_key: str, category_name: str) -> Optional[int]:
        """
        カテゴリー名からカテゴリーIDを取得
        
        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー
            category_name: カテゴリー名
            
        Returns:
            カテゴリーID。カテゴリーが存在しない場合はNone
        """
        categories = self.get_categories(project_id_or_key)
        for category in categories:
            if category.get("name") == category_name:
                return category.get("id")
        return None
    
    def get_milestones(self, project_id_or_key: str) -> List[Dict[str, Any]]:
        """
        マイルストーン一覧を取得
        
        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー
            
        Returns:
            マイルストーン一覧
        """
        try:
            response = self.milestone_api.get_milestone_list(project_id_or_key)
            return json.loads(response.text)
        except Exception as e:
            print(f"Error getting milestones for project {project_id_or_key}: {e}")
            return []
    
    def get_milestone_id_by_name(self, project_id_or_key: str, milestone_name: str) -> Optional[int]:
        """
        マイルストーン名からマイルストーンIDを取得
        
        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー
            milestone_name: マイルストーン名
            
        Returns:
            マイルストーンID。マイルストーンが存在しない場合はNone
        """
        milestones = self.get_milestones(project_id_or_key)
        for milestone in milestones:
            if milestone.get("name") == milestone_name:
                return milestone.get("id")
        return None
    
    def get_versions(self, project_id_or_key: str) -> List[Dict[str, Any]]:
        """
        バージョン一覧を取得
        
        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー
            
        Returns:
            バージョン一覧
        """
        try:
            response = self.version_api.get_version_milestone_list(project_id_or_key)
            return json.loads(response.text)
        except Exception as e:
            print(f"Error getting versions for project {project_id_or_key}: {e}")
            return []
    
    def get_version_id_by_name(self, project_id_or_key: str, version_name: str) -> Optional[int]:
        """
        バージョン名からバージョンIDを取得
        
        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー
            version_name: バージョン名
            
        Returns:
            バージョンID。バージョンが存在しない場合はNone
        """
        versions = self.get_versions(project_id_or_key)
        for version in versions:
            if version.get("name") == version_name:
                return version.get("id")
        return None
    
    def create_issue(self, project_id: Optional[int] = None, project_key: Optional[str] = None, 
                    summary: str = None, issue_type_id: Optional[int] = None, issue_type_name: Optional[str] = None,
                    priority_id: Optional[int] = None, priority_name: Optional[str] = None,
                    description: Optional[str] = None,
                    assignee_id: Optional[int] = None, assignee_name: Optional[str] = None,
                    category_id: Optional[List[int]] = None, category_name: Optional[List[str]] = None,
                    milestone_id: Optional[List[int]] = None, milestone_name: Optional[List[str]] = None,
                    version_id: Optional[List[int]] = None, version_name: Optional[List[str]] = None,
                    start_date: Optional[str] = None, 
                    due_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        課題を作成
        
        Args:
            project_id: プロジェクトID
            project_key: プロジェクトキー（project_idが指定されていない場合に使用）
            summary: 課題の件名
            issue_type_id: 課題の種別ID
            issue_type_name: 課題の種別名（issue_type_idが指定されていない場合に使用）
            priority_id: 優先度ID
            priority_name: 優先度名（priority_idが指定されていない場合に使用）
            description: 課題の詳細
            assignee_id: 担当者ID
            assignee_name: 担当者名（assignee_idが指定されていない場合に使用）
            category_id: カテゴリーIDのリスト
            category_name: カテゴリー名のリスト（category_idが指定されていない場合に使用）
            milestone_id: マイルストーンIDのリスト
            milestone_name: マイルストーン名のリスト（milestone_idが指定されていない場合に使用）
            version_id: 発生バージョンIDのリスト
            version_name: 発生バージョン名のリスト（version_idが指定されていない場合に使用）
            start_date: 開始日（yyyy-MM-dd形式）
            due_date: 期限日（yyyy-MM-dd形式）
            
        Returns:
            作成された課題情報。作成に失敗した場合はNone
        """
        try:
            # プロジェクトIDの解決
            if project_id is None and project_key is not None:
                project = self.get_project(project_key)
                if project:
                    project_id = project.get("id")
            
            if project_id is None:
                raise ValueError("Either project_id or project_key must be specified")
            
            # 課題種別IDの解決
            if issue_type_id is None and issue_type_name is not None:
                issue_types = self.get_issue_types(project_id)
                for issue_type in issue_types:
                    if issue_type.get("name") == issue_type_name:
                        issue_type_id = issue_type.get("id")
                        break
            
            # 優先度IDの解決
            if priority_id is None and priority_name is not None:
                priority_id = self.get_priority_id_by_name(priority_name)
            
            # 担当者IDの解決
            if assignee_id is None and assignee_name is not None:
                assignee_id = self.get_user_id_by_name(assignee_name)
            
            # カテゴリーIDの解決
            if category_id is None and category_name is not None:
                category_id = []
                for name in category_name:
                    cat_id = self.get_category_id_by_name(project_id, name)
                    if cat_id:
                        category_id.append(cat_id)
            
            # マイルストーンIDの解決
            if milestone_id is None and milestone_name is not None:
                milestone_id = []
                for name in milestone_name:
                    ms_id = self.get_milestone_id_by_name(project_id, name)
                    if ms_id:
                        milestone_id.append(ms_id)
            
            # 発生バージョンIDの解決
            if version_id is None and version_name is not None:
                version_id = []
                for name in version_name:
                    ver_id = self.get_version_id_by_name(project_id, name)
                    if ver_id:
                        version_id.append(ver_id)
            
            # 課題の作成
            params = {
                "project_id": project_id,
                "summary": summary,
                "description": description,
                "start_date": start_date,
                "due_date": due_date
            }
            
            if issue_type_id:
                params["issue_type_id"] = issue_type_id
            
            # 優先度IDが指定されていない場合は、デフォルト値（中）を設定
            # PyBacklogPyのIssue.add_issueメソッドではpriority_idが必須パラメータのため
            if priority_id:
                params["priority_id"] = priority_id
            else:
                # デフォルト値として「中」の優先度ID（3）を設定
                params["priority_id"] = 3
            if assignee_id:
                params["assignee_id"] = assignee_id
            if category_id:
                params["category_id"] = category_id
            if milestone_id:
                params["milestone_id"] = milestone_id
            if version_id:
                params["version_id"] = version_id
            
            response = self.issue_api.add_issue(**params)
            return json.loads(response.text)
        except Exception as e:
            print(f"Error creating issue: {e}")
            return None
    
    def update_issue(self, issue_id_or_key: str, summary: Optional[str] = None, 
                    description: Optional[str] = None, 
                    status_id: Optional[int] = None, status_name: Optional[str] = None,
                    priority_id: Optional[int] = None, priority_name: Optional[str] = None,
                    assignee_id: Optional[int] = None, assignee_name: Optional[str] = None,
                    category_id: Optional[List[int]] = None, category_name: Optional[List[str]] = None,
                    milestone_id: Optional[List[int]] = None, milestone_name: Optional[List[str]] = None,
                    version_id: Optional[List[int]] = None, version_name: Optional[List[str]] = None,
                    start_date: Optional[str] = None, 
                    due_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        課題を更新
        
        Args:
            issue_id_or_key: 課題IDまたは課題キー
            summary: 課題の件名
            description: 課題の詳細
            status_id: ステータスID
            status_name: ステータス名（status_idが指定されていない場合に使用）
            priority_id: 優先度ID
            priority_name: 優先度名（priority_idが指定されていない場合に使用）
            assignee_id: 担当者ID
            assignee_name: 担当者名（assignee_idが指定されていない場合に使用）
            category_id: カテゴリーIDのリスト
            category_name: カテゴリー名のリスト（category_idが指定されていない場合に使用）
            milestone_id: マイルストーンIDのリスト
            milestone_name: マイルストーン名のリスト（milestone_idが指定されていない場合に使用）
            version_id: 発生バージョンIDのリスト
            version_name: 発生バージョン名のリスト（version_idが指定されていない場合に使用）
            start_date: 開始日（yyyy-MM-dd形式）
            due_date: 期限日（yyyy-MM-dd形式）
            
        Returns:
            更新された課題情報。更新に失敗した場合はNone
        """
        try:
            # 課題情報の取得（プロジェクトIDを取得するため）
            issue = self.get_issue(issue_id_or_key)
            if not issue:
                raise ValueError(f"Issue with ID or key {issue_id_or_key} not found")
            
            project_id = issue.get("projectId")
            
            # ステータスIDの解決
            if status_id is None and status_name is not None:
                status_id = self.get_status_id_by_name(project_id, status_name)
            
            # 優先度IDの解決
            if priority_id is None and priority_name is not None:
                priority_id = self.get_priority_id_by_name(priority_name)
            
            # 担当者IDの解決
            if assignee_id is None and assignee_name is not None:
                assignee_id = self.get_user_id_by_name(assignee_name)
            
            # カテゴリーIDの解決
            if category_id is None and category_name is not None:
                category_id = []
                for name in category_name:
                    cat_id = self.get_category_id_by_name(project_id, name)
                    if cat_id:
                        category_id.append(cat_id)
            
            # マイルストーンIDの解決
            if milestone_id is None and milestone_name is not None:
                milestone_id = []
                for name in milestone_name:
                    ms_id = self.get_milestone_id_by_name(project_id, name)
                    if ms_id:
                        milestone_id.append(ms_id)
            
            # 発生バージョンIDの解決
            if version_id is None and version_name is not None:
                version_id = []
                for name in version_name:
                    ver_id = self.get_version_id_by_name(project_id, name)
                    if ver_id:
                        version_id.append(ver_id)
            
            # 課題の更新
            params = {
                "issue_id_or_key": issue_id_or_key,
                "summary": summary,
                "description": description,
                "start_date": start_date,
                "due_date": due_date
            }
            
            if status_id:
                params["status_id"] = status_id
            if priority_id:
                params["priority_id"] = priority_id
            if assignee_id:
                params["assignee_id"] = assignee_id
            if category_id:
                params["category_id"] = category_id
            if milestone_id:
                params["milestone_id"] = milestone_id
            if version_id:
                params["version_id"] = version_id
            
            response = self.issue_api.update_issue(**params)
            return json.loads(response.text)
        except Exception as e:
            print(f"Error updating issue {issue_id_or_key}: {e}")
            return None
    
    def delete_issue(self, issue_id_or_key: str) -> bool:
        """
        課題を削除
        
        Args:
            issue_id_or_key: 課題IDまたは課題キー
            
        Returns:
            削除に成功した場合はTrue、失敗した場合はFalse
        """
        try:
            response = self.issue_api.delete_issue(issue_id_or_key)
            return response.ok
        except Exception as e:
            print(f"Error deleting issue {issue_id_or_key}: {e}")
            return False
    
    def add_comment(self, issue_id_or_key: str, content: str) -> Optional[Dict[str, Any]]:
        """
        課題にコメントを追加
        
        Args:
            issue_id_or_key: 課題IDまたは課題キー
            content: コメント内容
            
        Returns:
            追加されたコメント情報。追加に失敗した場合はNone
        """
        try:
            response = self.issue_comment_api.add_comment(
                issue_id_or_key=issue_id_or_key,
                content=content
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error adding comment to issue {issue_id_or_key}: {e}")
            return None
    
    def get_issue_comments(self, issue_id_or_key: str, count: int = 20) -> List[Dict[str, Any]]:
        """
        課題のコメント一覧を取得
        
        Args:
            issue_id_or_key: 課題IDまたは課題キー
            count: 取得件数（デフォルト20件）
            
        Returns:
            コメント一覧
        """
        try:
            response = self.issue_comment_api.get_comment_list(
                issue_id_or_key=issue_id_or_key,
                count=count
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error getting comments for issue {issue_id_or_key}: {e}")
            return []
    
    def get_issue_types(self, project_id_or_key: str) -> List[Dict[str, Any]]:
        """
        課題の種別一覧を取得
        
        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー
            
        Returns:
            課題の種別一覧
        """
        try:
            response = self.issue_type_api.get_issue_type_list(project_id_or_key)
            return json.loads(response.text)
        except Exception as e:
            print(f"Error getting issue types for project {project_id_or_key}: {e}")
            return []
