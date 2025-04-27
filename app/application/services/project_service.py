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
