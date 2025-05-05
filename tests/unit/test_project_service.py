"""
プロジェクト管理サービスのユニットテスト
"""
import pytest
from unittest.mock import Mock, patch
from app.application.services.project_service import ProjectService


class TestProjectService:
    """プロジェクト管理サービスのテストクラス"""
    
    def test_get_project_returns_dict(self, mock_backlog_client):
        """プロジェクト情報を取得するメソッドが辞書を返すことを確認するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.get_project.return_value = {
            "id": 1, "projectKey": "TEST1", "name": "テストプロジェクト1"
        }
        
        # テスト対象のサービスをインスタンス化
        project_service = ProjectService(backlog_client=mock_backlog_client)
        
        # プロジェクト情報を取得
        project = project_service.get_project("TEST1")
        
        # モックが正しいパラメータで呼ばれたことを確認
        mock_backlog_client.get_project.assert_called_once_with("TEST1")
        
        # 結果の検証
        assert isinstance(project, dict)
        assert project["id"] == 1
        assert project["projectKey"] == "TEST1"
        assert project["name"] == "テストプロジェクト1"
    
    def test_get_project_handles_not_found(self, mock_backlog_client):
        """存在しないプロジェクトの場合の処理をテスト"""
        # モックの戻り値をNoneに設定
        mock_backlog_client.get_project.return_value = None
        
        # テスト対象のサービスをインスタンス化
        project_service = ProjectService(backlog_client=mock_backlog_client)
        
        # プロジェクト情報を取得
        project = project_service.get_project("NOT-EXIST")
        
        # 結果の検証
        assert project is None
    
    def test_get_project_handles_error(self, mock_backlog_client):
        """エラー発生時の処理をテスト"""
        # モックがエラーを発生させるように設定
        mock_backlog_client.get_project.side_effect = Exception("API Error")
        
        # テスト対象のサービスをインスタンス化
        project_service = ProjectService(backlog_client=mock_backlog_client)
        
        # エラーが発生することを確認
        with pytest.raises(Exception) as excinfo:
            project_service.get_project("TEST1")
        
        # エラーメッセージを確認
        assert "Failed to get project" in str(excinfo.value)

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
