"""
プロジェクト管理APIの統合テスト
"""
import pytest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app


class TestProjectAPI:
    """プロジェクト管理APIのテストクラス"""

    @pytest.fixture
    def client(self):
        """テストクライアントを作成するフィクスチャ"""
        return TestClient(app)

    def test_get_projects_returns_200(self, client, mock_backlog_client):
        """プロジェクト一覧を取得するAPIが200を返すことを確認するテスト"""
        # 環境変数をモック
        with patch.dict(os.environ, {"BACKLOG_API_KEY": "dummy_key", "BACKLOG_SPACE": "dummy_space"}):
            # BacklogClientのget_projectsメソッドをモック
            with patch("app.presentation.api.project_router.BacklogClient") as mock_client_class:
                mock_client_class.return_value = mock_backlog_client
                
                # APIを呼び出し
                response = client.get("/api/projects")
            
            # 結果の検証
            assert response.status_code == 200
            assert isinstance(response.json(), list)
            assert len(response.json()) == 2

    def test_get_projects_returns_json(self, client, mock_backlog_client):
        """プロジェクト一覧を取得するAPIがJSONを返すことを確認するテスト"""
        # 環境変数をモック
        with patch.dict(os.environ, {"BACKLOG_API_KEY": "dummy_key", "BACKLOG_SPACE": "dummy_space"}):
            # BacklogClientのget_projectsメソッドをモック
            with patch("app.presentation.api.project_router.BacklogClient") as mock_client_class:
                mock_client_class.return_value = mock_backlog_client
                
                # APIを呼び出し
                response = client.get("/api/projects")
            
            # 結果の検証
            assert response.headers["Content-Type"] == "application/json"
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 2
            assert "id" in data[0]
            assert "projectKey" in data[0]
            assert "name" in data[0]

    def test_get_projects_handles_error(self, client):
        """エラー発生時の処理をテスト"""
        # 環境変数をモック
        with patch.dict(os.environ, {"BACKLOG_API_KEY": "dummy_key", "BACKLOG_SPACE": "dummy_space"}):
            # ProjectServiceのget_projectsメソッドをモック
            with patch("app.presentation.api.project_router.get_project_service") as mock_get_service:
                mock_get_service.side_effect = Exception("Service Error")
                
                # APIを呼び出し
                response = client.get("/api/projects")
            
            # エラーが発生した場合は500を返すことを確認
            assert response.status_code == 500
            assert "detail" in response.json()
