"""
課題管理の結合テスト
"""
import os
import pytest
from dotenv import load_dotenv
from app.infrastructure.backlog.backlog_client import BacklogClient


class TestIssueIntegration:
    """課題管理の結合テストクラス"""

    @pytest.fixture(scope="class")
    def env_vars(self):
        """環境変数を読み込むフィクスチャ"""
        load_dotenv()
        return {
            "api_key": os.getenv("BACKLOG_API_KEY"),
            "space": os.getenv("BACKLOG_SPACE"),
            "project": os.getenv("BACKLOG_PROJECT")
        }

    @pytest.fixture(scope="class")
    def backlog_client(self, env_vars):
        """BacklogClientのインスタンスを作成するフィクスチャ"""
        return BacklogClient(
            api_key=env_vars["api_key"],
            space=env_vars["space"]
        )

    @pytest.fixture(scope="class")
    def test_issue(self, backlog_client, env_vars):
        """テスト用の課題を作成するフィクスチャ"""
        # プロジェクトIDを取得
        projects = backlog_client.get_projects()
        project_id = None
        for project in projects:
            if project["projectKey"] == env_vars["project"]:
                project_id = project["id"]
                break
        
        if not project_id:
            pytest.skip(f"Project {env_vars['project']} not found")
        
        # 課題の種別IDを取得
        issue_types = backlog_client.get_issue_types(env_vars["project"])
        if not issue_types:
            pytest.skip("No issue types found")
        issue_type_id = issue_types[0]["id"]
        
        # 課題を作成
        issue = backlog_client.create_issue(
            project_id=project_id,
            summary="結合テスト用課題",
            issue_type_id=issue_type_id,
            priority_id=3,  # 通常
            description="これは結合テスト用の課題です。"
        )
        
        yield issue
        
        # テスト後にクリーンアップ
        try:
            backlog_client.delete_issue(issue["issueKey"])
        except Exception as e:
            print(f"Failed to delete test issue: {e}")

    @pytest.mark.skipif(
        not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE") or not os.getenv("BACKLOG_PROJECT"),
        reason="Backlog API環境変数が設定されていません"
    )
    def test_get_issues_from_real_api(self, backlog_client):
        """実際のBacklog APIから課題一覧を取得するテスト"""
        # 課題一覧を取得
        issues = backlog_client.get_issues()
        
        # 結果の検証
        assert isinstance(issues, list)
        # 課題が存在する場合のみ検証
        if len(issues) > 0:
            assert "id" in issues[0]
            assert "issueKey" in issues[0]
            assert "summary" in issues[0]

    @pytest.mark.skipif(
        not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE") or not os.getenv("BACKLOG_PROJECT"),
        reason="Backlog API環境変数が設定されていません"
    )
    def test_get_issue_by_key(self, backlog_client, test_issue):
        """特定の課題キーで課題を取得するテスト"""
        # 課題を取得
        issue = backlog_client.get_issue(test_issue["issueKey"])
        
        # 結果の検証
        assert issue is not None
        assert "id" in issue
        assert "issueKey" in issue
        assert issue["issueKey"] == test_issue["issueKey"]
        assert issue["summary"] == "結合テスト用課題"

    @pytest.mark.skipif(
        not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE") or not os.getenv("BACKLOG_PROJECT"),
        reason="Backlog API環境変数が設定されていません"
    )
    def test_update_issue(self, backlog_client, test_issue):
        """課題を更新するテスト"""
        # 課題を更新
        updated_issue = backlog_client.update_issue(
            issue_id_or_key=test_issue["issueKey"],
            summary="更新された結合テスト用課題"
        )
        
        # 結果の検証
        assert updated_issue is not None
        assert "id" in updated_issue
        assert "issueKey" in updated_issue
        assert updated_issue["issueKey"] == test_issue["issueKey"]
        assert updated_issue["summary"] == "更新された結合テスト用課題"
    
    @pytest.mark.skipif(
        not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE") or not os.getenv("BACKLOG_PROJECT"),
        reason="Backlog API環境変数が設定されていません"
    )
    def test_update_issue_with_name_parameters(self, backlog_client, test_issue):
        """名前ベースのパラメータで課題を更新するテスト"""
        # 課題を更新
        updated_issue = backlog_client.update_issue(
            issue_id_or_key=test_issue["issueKey"],
            summary="名前ベースで更新された結合テスト用課題",
            status_name="処理中"  # ステータス名で指定
        )
        
        # 結果の検証
        assert updated_issue is not None
        assert "id" in updated_issue
        assert "issueKey" in updated_issue
        assert updated_issue["issueKey"] == test_issue["issueKey"]
        assert updated_issue["summary"] == "名前ベースで更新された結合テスト用課題"
        assert "status" in updated_issue
        assert updated_issue["status"]["name"] == "処理中"

    @pytest.mark.skipif(
        not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE") or not os.getenv("BACKLOG_PROJECT"),
        reason="Backlog API環境変数が設定されていません"
    )
    def test_add_and_get_comments(self, backlog_client, test_issue):
        """コメントを追加して取得するテスト"""
        # コメントを追加
        comment = backlog_client.add_comment(
            issue_id_or_key=test_issue["issueKey"],
            content="これは結合テスト用のコメントです。"
        )
        
        # 結果の検証
        assert comment is not None
        assert "id" in comment
        assert "content" in comment
        assert comment["content"] == "これは結合テスト用のコメントです。"
        
        # コメント一覧を取得
        comments = backlog_client.get_issue_comments(test_issue["issueKey"])
        
        # 結果の検証
        assert isinstance(comments, list)
        assert len(comments) > 0
        # 最新のコメントが追加したコメントであることを確認
        assert comments[0]["id"] == comment["id"]
        assert comments[0]["content"] == "これは結合テスト用のコメントです。"

    @pytest.mark.skipif(
        not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE") or not os.getenv("BACKLOG_PROJECT"),
        reason="Backlog API環境変数が設定されていません"
    )
    def test_create_and_delete_issue(self, backlog_client, env_vars):
        """課題を作成して削除するテスト"""
        # プロジェクトIDを取得
        projects = backlog_client.get_projects()
        project_id = None
        for project in projects:
            if project["projectKey"] == env_vars["project"]:
                project_id = project["id"]
                break
        
        if not project_id:
            pytest.skip(f"Project {env_vars['project']} not found")
        
        # 課題の種別IDを取得
        issue_types = backlog_client.get_issue_types(env_vars["project"])
        if not issue_types:
            pytest.skip("No issue types found")
        issue_type_id = issue_types[0]["id"]
        
        # 課題を作成
        issue = backlog_client.create_issue(
            project_id=project_id,
            summary="削除テスト用課題",
            issue_type_id=issue_type_id,
            priority_id=3,  # 通常
            description="これは削除テスト用の課題です。"
        )
        
        # 結果の検証
        assert issue is not None
        assert "id" in issue
        assert "issueKey" in issue
        assert issue["summary"] == "削除テスト用課題"
        
        # 課題を削除
        result = backlog_client.delete_issue(issue["issueKey"])
        
        # 結果の検証
        assert result is True
        
        # 削除されたことを確認
        deleted_issue = backlog_client.get_issue(issue["issueKey"])
        # 課題が削除されている場合、エラーオブジェクトが返されるか、Noneが返される
        if deleted_issue is not None:
            assert "errors" in deleted_issue
    
    @pytest.mark.skipif(
        not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE") or not os.getenv("BACKLOG_PROJECT"),
        reason="Backlog API環境変数が設定されていません"
    )
    def test_create_issue_with_name_parameters(self, backlog_client, env_vars):
        """名前ベースのパラメータで課題を作成するテスト"""
        # 課題を作成
        issue = backlog_client.create_issue(
            project_key=env_vars["project"],  # プロジェクトキーで指定
            summary="名前ベースの結合テスト用課題",
            issue_type_name="タスク",  # 課題種別名で指定（実際の環境に合わせて調整が必要）
            priority_name="中",  # 優先度名で指定
            description="これは名前ベースのパラメータによる結合テスト用の課題です。"
        )
        
        # 結果の検証
        assert issue is not None
        assert "id" in issue
        assert "issueKey" in issue
        assert issue["summary"] == "名前ベースの結合テスト用課題"
        
        # クリーンアップ
        backlog_client.delete_issue(issue["issueKey"])
