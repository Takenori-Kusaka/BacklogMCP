"""
Backlog APIクライアント
"""
from typing import Dict, List, Optional, Any
import os
from pybacklogpy.BacklogConfigure import BacklogComConfigure
from pybacklogpy.Project import Project


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
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """
        プロジェクト一覧を取得
        
        Returns:
            プロジェクト一覧
        """
        response = self.project_api.get_projects()
        return response
    
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
            return response
        except Exception as e:
            # プロジェクトが存在しない場合などのエラー処理
            print(f"Error getting project {project_key}: {e}")
            return None
