"""
プロジェクト管理サービスのユニットテスト
"""
import pytest
from unittest.mock import Mock, patch
from app.application.services.project_service import ProjectService


class TestProjectService:
    """プロジェクト管理サービスのテストクラス"""

    def test_get_projects_returns_list(self, project_service):
        """プロジェクト一覧を取得するメソッドがリストを返すことを確認するテスト"""
        # プロジェクト一覧を取得
        projects = project_service.get_projects()
        
        # 結果の検証
        assert isinstance(projects, list)
        assert len(projects) == 2
        assert projects[0]["id"] == 1
        assert projects[0]["projectKey"] == "TEST1"
        assert projects[0]["name"] == "テストプロジェクト1"

    def test_get_projects_handles_empty_response(self, mock_backlog_client):
        """プロジェクト一覧が空の場合の処理をテスト"""
        # モックの戻り値を空リストに設定
        mock_backlog_client.get_projects.return_value = []
        
        # テスト対象のサービスをインスタンス化
        project_service = ProjectService(backlog_client=mock_backlog_client)
        
        # プロジェクト一覧を取得
        projects = project_service.get_projects()
        
        # 結果の検証
        assert isinstance(projects, list)
        assert len(projects) == 0

    def test_get_projects_handles_error(self, mock_backlog_client):
        """エラー発生時の処理をテスト"""
        # モックがエラーを発生させるように設定
        mock_backlog_client.get_projects.side_effect = Exception("API Error")
        
        # テスト対象のサービスをインスタンス化
        project_service = ProjectService(backlog_client=mock_backlog_client)
        
        # エラーが発生することを確認
        with pytest.raises(Exception) as excinfo:
            project_service.get_projects()
        
        # エラーメッセージを確認
        assert "Failed to get projects" in str(excinfo.value)
