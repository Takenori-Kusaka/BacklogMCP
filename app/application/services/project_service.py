"""
プロジェクト管理サービス
"""
from typing import Dict, List, Optional, Any
from app.infrastructure.backlog.backlog_client import BacklogClient


class ProjectService:
    """
    プロジェクト管理サービス
    
    プロジェクト関連の業務ロジックを実装するサービスクラス
    """
    
    def __init__(self, backlog_client: BacklogClient):
        """
        初期化
        
        Args:
            backlog_client: Backlogクライアント
        """
        self.backlog_client = backlog_client
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """
        プロジェクト一覧を取得
        
        Returns:
            プロジェクト一覧
        
        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            projects = self.backlog_client.get_projects()
            return projects
        except Exception as e:
            # エラーログの出力など
            print(f"Error getting projects: {e}")
            # 呼び出し元でハンドリングできるように例外を再スロー
            raise Exception(f"Failed to get projects: {e}") from e
    
    def get_project(self, project_key: str) -> Optional[Dict[str, Any]]:
        """
        プロジェクトを取得
        
        Args:
            project_key: プロジェクトキー
            
        Returns:
            プロジェクト情報。プロジェクトが存在しない場合はNone
            
        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            project = self.backlog_client.get_project(project_key)
            return project
        except Exception as e:
            # エラーログの出力など
            print(f"Error getting project {project_key}: {e}")
            # 呼び出し元でハンドリングできるように例外を再スロー
            raise Exception(f"Failed to get project {project_key}: {e}") from e
    
    def get_project_statuses(self, project_key: str) -> List[Dict[str, Any]]:
        """
        プロジェクトのステータス一覧を取得
        
        Args:
            project_key: プロジェクトキー
            
        Returns:
            ステータス一覧
            
        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            statuses = self.backlog_client.get_statuses(project_key)
            return statuses
        except Exception as e:
            # エラーログの出力など
            print(f"Error getting statuses for project {project_key}: {e}")
            # 呼び出し元でハンドリングできるように例外を再スロー
            raise Exception(f"Failed to get statuses for project {project_key}: {e}") from e
    
    def get_project_issue_types(self, project_key: str) -> List[Dict[str, Any]]:
        """
        プロジェクトの課題種別一覧を取得
        
        Args:
            project_key: プロジェクトキー
            
        Returns:
            課題種別一覧
            
        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            issue_types = self.backlog_client.get_issue_types(project_key)
            return issue_types
        except Exception as e:
            # エラーログの出力など
            print(f"Error getting issue types for project {project_key}: {e}")
            # 呼び出し元でハンドリングできるように例外を再スロー
            raise Exception(f"Failed to get issue types for project {project_key}: {e}") from e
    
    def get_project_categories(self, project_key: str) -> List[Dict[str, Any]]:
        """
        プロジェクトのカテゴリー一覧を取得
        
        Args:
            project_key: プロジェクトキー
            
        Returns:
            カテゴリー一覧
            
        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            categories = self.backlog_client.get_categories(project_key)
            return categories
        except Exception as e:
            # エラーログの出力など
            print(f"Error getting categories for project {project_key}: {e}")
            # 呼び出し元でハンドリングできるように例外を再スロー
            raise Exception(f"Failed to get categories for project {project_key}: {e}") from e
    
    def get_project_milestones(self, project_key: str) -> List[Dict[str, Any]]:
        """
        プロジェクトのマイルストーン一覧を取得
        
        Args:
            project_key: プロジェクトキー
            
        Returns:
            マイルストーン一覧
            
        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            milestones = self.backlog_client.get_milestones(project_key)
            return milestones
        except Exception as e:
            # エラーログの出力など
            print(f"Error getting milestones for project {project_key}: {e}")
            # 呼び出し元でハンドリングできるように例外を再スロー
            raise Exception(f"Failed to get milestones for project {project_key}: {e}") from e
    
    def get_project_versions(self, project_key: str) -> List[Dict[str, Any]]:
        """
        プロジェクトの発生バージョン一覧を取得
        
        Args:
            project_key: プロジェクトキー
            
        Returns:
            発生バージョン一覧
            
        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            versions = self.backlog_client.get_versions(project_key)
            return versions
        except Exception as e:
            # エラーログの出力など
            print(f"Error getting versions for project {project_key}: {e}")
            # 呼び出し元でハンドリングできるように例外を再スロー
            raise Exception(f"Failed to get versions for project {project_key}: {e}") from e
