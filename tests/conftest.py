"""
pytest用の共通フィクスチャ
"""
import pytest
from unittest.mock import Mock
from app.infrastructure.backlog.backlog_client import BacklogClient
from app.application.services.project_service import ProjectService


@pytest.fixture
def mock_backlog_client():
    """
    モックのBacklogクライアント
    
    Returns:
        Mock: モックのBacklogクライアント
    """
    mock_client = Mock(spec=BacklogClient)
    
    # プロジェクト一覧を取得するメソッドのモック
    mock_client.get_projects.return_value = [
        {"id": 1, "projectKey": "TEST1", "name": "テストプロジェクト1"},
        {"id": 2, "projectKey": "TEST2", "name": "テストプロジェクト2"}
    ]
    
    # プロジェクトを取得するメソッドのモック
    mock_client.get_project.return_value = {
        "id": 1, "projectKey": "TEST1", "name": "テストプロジェクト1"
    }
    
    return mock_client


@pytest.fixture
def project_service(mock_backlog_client):
    """
    プロジェクト管理サービス
    
    Args:
        mock_backlog_client: モックのBacklogクライアント
        
    Returns:
        ProjectService: プロジェクト管理サービス
    """
    return ProjectService(backlog_client=mock_backlog_client)
