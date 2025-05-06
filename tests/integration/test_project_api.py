"""
プロジェクト管理の結合テスト
"""

import os

import pytest
from dotenv import load_dotenv

from app.infrastructure.backlog.backlog_client import BacklogClient


class TestProjectIntegration:
    """プロジェクト管理の結合テストクラス"""

    @pytest.fixture(scope="class")
    def env_vars(self) -> dict[str, str | None]:
        """環境変数を読み込むフィクスチャ"""
        load_dotenv()
        return {
            "api_key": os.getenv("BACKLOG_API_KEY"),
            "space": os.getenv("BACKLOG_SPACE"),
            "project": os.getenv("BACKLOG_PROJECT"),
        }

    @pytest.mark.skipif(
        not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE"),
        reason="Backlog API環境変数が設定されていません",
    )
    def test_get_projects_from_real_api(self, env_vars: dict[str, str | None]) -> None:
        """実際のBacklog APIからプロジェクト一覧を取得するテスト"""
        # テスト対象のクライアントをインスタンス化
        api_key = env_vars["api_key"]
        space = env_vars["space"]
        if api_key is None or space is None:
            pytest.skip("API Key または Space が設定されていません")
        backlog_client = BacklogClient(api_key=api_key, space=space)

        # プロジェクト一覧を取得
        projects = backlog_client.get_projects()

        # 結果の検証
        assert isinstance(projects, list)
        # プロジェクトが存在する場合のみ検証
        if len(projects) > 0:
            assert "id" in projects[0]
            assert "projectKey" in projects[0]
            assert "name" in projects[0]

    @pytest.mark.skipif(
        not os.getenv("BACKLOG_API_KEY")
        or not os.getenv("BACKLOG_SPACE")
        or not os.getenv("BACKLOG_PROJECT"),
        reason="Backlog API環境変数が設定されていません",
    )
    def test_get_project_by_key(self, env_vars: dict[str, str | None]) -> None:
        """特定のプロジェクトキーでプロジェクトを取得するテスト"""
        # テスト対象のクライアントをインスタンス化
        api_key = env_vars["api_key"]
        space = env_vars["space"]
        project_key = env_vars["project"]
        if api_key is None or space is None or project_key is None:
            pytest.skip("API Key, Space または Project が設定されていません")
        backlog_client = BacklogClient(api_key=api_key, space=space)

        # プロジェクトを取得
        project = backlog_client.get_project(project_key)

        # 結果の検証
        assert project is not None
        assert "id" in project
        assert "projectKey" in project
        assert project["projectKey"] == env_vars["project"]
