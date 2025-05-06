"""
課題管理サービスのユニットテスト
"""

from unittest.mock import Mock, patch

import pytest

from tests.mocks import MockIssueService


class TestIssueService:
    """課題管理サービスのテストクラス"""

    def test_get_issues_returns_list(self, mock_backlog_client: Mock) -> None:
        """課題一覧を取得するメソッドがリストを返すことを確認するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.get_issues.return_value = [
            {"id": 1, "issueKey": "TEST-1", "summary": "テスト課題1"},
            {"id": 2, "issueKey": "TEST-2", "summary": "テスト課題2"},
        ]

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # 課題一覧を取得
        issues = issue_service.get_issues()

        # 結果の検証
        assert isinstance(issues, list)
        assert len(issues) == 2
        assert issues[0]["id"] == 1
        assert issues[0]["issueKey"] == "TEST-1"
        assert issues[0]["summary"] == "テスト課題1"

    def test_get_issues_with_parameters(self, mock_backlog_client: Mock) -> None:
        """パラメータ付きで課題一覧を取得するメソッドのテスト"""
        # モックの戻り値を設定
        mock_backlog_client.get_issues.return_value = [
            {"id": 1, "issueKey": "TEST-1", "summary": "テスト課題1"}
        ]

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # パラメータ付きで課題一覧を取得
        issues = issue_service.get_issues(project_id=1, keyword="テスト", count=10)

        # モックが正しいパラメータで呼ばれたことを確認
        mock_backlog_client.get_issues.assert_called_once_with(
            project_id=1, status_id=None, assignee_id=None, keyword="テスト", count=10
        )

        # 結果の検証
        assert isinstance(issues, list)
        assert len(issues) == 1
        assert issues[0]["id"] == 1
        assert issues[0]["issueKey"] == "TEST-1"
        assert issues[0]["summary"] == "テスト課題1"

    def test_get_issues_with_status_id(self, mock_backlog_client: Mock) -> None:
        """ステータスIDによるフィルタリングのテスト"""
        # モックの戻り値を設定
        mock_backlog_client.get_issues.return_value = [
            {
                "id": 1,
                "issueKey": "TEST-1",
                "summary": "テスト課題1",
                "status": {"id": 2, "name": "処理中"},
            }
        ]

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # ステータスIDでフィルタリングして課題一覧を取得
        issues = issue_service.get_issues(status_id=2)

        # モックが正しいパラメータで呼ばれたことを確認
        mock_backlog_client.get_issues.assert_called_once_with(
            project_id=None, status_id=2, assignee_id=None, keyword=None, count=20
        )

        # 結果の検証
        assert isinstance(issues, list)
        assert len(issues) == 1
        assert issues[0]["status"]["id"] == 2
        assert issues[0]["status"]["name"] == "処理中"

    def test_get_issues_with_assignee_id(self, mock_backlog_client: Mock) -> None:
        """担当者IDによるフィルタリングのテスト"""
        # モックの戻り値を設定
        mock_backlog_client.get_issues.return_value = [
            {
                "id": 1,
                "issueKey": "TEST-1",
                "summary": "テスト課題1",
                "assignee": {"id": 123, "name": "テストユーザー"},
            }
        ]

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # 担当者IDでフィルタリングして課題一覧を取得
        issues = issue_service.get_issues(assignee_id=123)

        # モックが正しいパラメータで呼ばれたことを確認
        mock_backlog_client.get_issues.assert_called_once_with(
            project_id=None, status_id=None, assignee_id=123, keyword=None, count=20
        )

        # 結果の検証
        assert isinstance(issues, list)
        assert len(issues) == 1
        assert issues[0]["assignee"]["id"] == 123
        assert issues[0]["assignee"]["name"] == "テストユーザー"

    def test_get_issues_handles_empty_response(self, mock_backlog_client: Mock) -> None:
        """課題一覧が空の場合の処理をテスト"""
        # モックの戻り値を空リストに設定
        mock_backlog_client.get_issues.return_value = []

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # 課題一覧を取得
        issues = issue_service.get_issues()

        # 結果の検証
        assert isinstance(issues, list)
        assert len(issues) == 0

    def test_get_issues_handles_error(self, mock_backlog_client: Mock) -> None:
        """エラー発生時の処理をテスト"""
        # モックがエラーを発生させるように設定
        mock_backlog_client.get_issues.side_effect = Exception("API Error")

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # エラーが発生することを確認
        with pytest.raises(Exception) as excinfo:
            issue_service.get_issues()

        # エラーメッセージを確認
        assert "Failed to get issues" in str(excinfo.value)

    def test_get_issue_returns_dict(self, mock_backlog_client: Mock) -> None:
        """課題情報を取得するメソッドが辞書を返すことを確認するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.get_issue.return_value = {
            "id": 1,
            "issueKey": "TEST-1",
            "summary": "テスト課題1",
        }

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # 課題情報を取得
        issue = issue_service.get_issue("TEST-1")

        # 結果の検証
        assert isinstance(issue, dict)
        assert issue["id"] == 1
        assert issue["issueKey"] == "TEST-1"
        assert issue["summary"] == "テスト課題1"

    def test_get_issue_handles_not_found(self, mock_backlog_client: Mock) -> None:
        """存在しない課題の場合の処理をテスト"""
        # モックの戻り値をNoneに設定
        mock_backlog_client.get_issue.return_value = None

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # 課題情報を取得
        issue = issue_service.get_issue("NOT-EXIST")

        # 結果の検証
        assert issue is None

    def test_get_issue_handles_error(self, mock_backlog_client: Mock) -> None:
        """エラー発生時の処理をテスト"""
        # モックがエラーを発生させるように設定
        mock_backlog_client.get_issue.side_effect = Exception("API Error")

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # エラーが発生することを確認
        with pytest.raises(Exception) as excinfo:
            issue_service.get_issue("TEST-1")

        # エラーメッセージを確認
        assert "Failed to get issue" in str(excinfo.value)

    def test_create_issue_returns_dict(self, mock_backlog_client: Mock) -> None:
        """課題を作成するメソッドが辞書を返すことを確認するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.create_issue.return_value = {
            "id": 1,
            "issueKey": "TEST-1",
            "summary": "新しい課題",
        }

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # 課題を作成
        issue = issue_service.create_issue(
            project_id=1,
            summary="新しい課題",
            issue_type_id=2,
            priority_id=3,
            description="課題の詳細",
        )

        # 結果の検証
        assert isinstance(issue, dict)
        assert issue["id"] == 1
        assert issue["issueKey"] == "TEST-1"
        assert issue["summary"] == "新しい課題"

    def test_create_issue_with_name_parameters(self, mock_backlog_client: Mock) -> None:
        """名前ベースのパラメータで課題を作成するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.create_issue.return_value = {
            "id": 1,
            "issueKey": "TEST-1",
            "summary": "名前ベースの課題",
        }
        mock_backlog_client.get_project.return_value = {
            "id": 1,
            "projectKey": "TEST1",
            "name": "テストプロジェクト1",
        }
        mock_backlog_client.get_priority_id_by_name.return_value = 2
        mock_backlog_client.get_user_id_by_name.return_value = 1

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # 名前ベースのパラメータで課題を作成
        issue = issue_service.create_issue(
            project_key="TEST1",
            summary="名前ベースの課題",
            issue_type_name="バグ",
            priority_name="高",
            assignee_name="テストユーザー1",
            category_name=["フロントエンド"],
            milestone_name=["5月リリース"],
            version_name=["v1.0.0"],
            description="名前ベースのパラメータによる課題",
        )

        # 結果の検証
        assert isinstance(issue, dict)
        assert issue["id"] == 1
        assert issue["issueKey"] == "TEST-1"
        assert issue["summary"] == "名前ベースの課題"

    def test_create_issue_handles_error(self, mock_backlog_client: Mock) -> None:
        """エラー発生時の処理をテスト"""
        # モックがエラーを発生させるように設定
        mock_backlog_client.create_issue.side_effect = Exception("API Error")

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # エラーが発生することを確認
        with pytest.raises(Exception) as excinfo:
            issue_service.create_issue(
                project_id=1, summary="新しい課題", issue_type_id=2, priority_id=3
            )

        # エラーメッセージを確認
        assert "Failed to create issue" in str(excinfo.value)

    def test_update_issue_returns_dict(self, mock_backlog_client: Mock) -> None:
        """課題を更新するメソッドが辞書を返すことを確認するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.update_issue.return_value = {
            "id": 1,
            "issueKey": "TEST-1",
            "summary": "更新された課題",
        }

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # 課題を更新
        issue = issue_service.update_issue(
            issue_id_or_key="TEST-1", summary="更新された課題", status_id=2
        )

        # 結果の検証
        assert isinstance(issue, dict)
        assert issue["id"] == 1
        assert issue["issueKey"] == "TEST-1"
        assert issue["summary"] == "更新された課題"

    def test_update_issue_with_name_parameters(self, mock_backlog_client: Mock) -> None:
        """名前ベースのパラメータで課題を更新するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.update_issue.return_value = {
            "id": 1,
            "issueKey": "TEST-1",
            "summary": "名前ベースで更新された課題",
            "status": {"id": 2, "name": "処理中"},
            "assignee": {"id": 1, "name": "テストユーザー1"},
        }
        mock_backlog_client.get_issue.return_value = {
            "id": 1,
            "issueKey": "TEST-1",
            "projectId": 1,
        }
        mock_backlog_client.get_status_id_by_name.return_value = 2
        mock_backlog_client.get_priority_id_by_name.return_value = 2
        mock_backlog_client.get_user_id_by_name.return_value = 1

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # 名前ベースのパラメータで課題を更新
        issue = issue_service.update_issue(
            issue_id_or_key="TEST-1",
            summary="名前ベースで更新された課題",
            status_name="処理中",
            priority_name="高",
            assignee_name="テストユーザー1",
            category_name=["フロントエンド"],
            milestone_name=["5月リリース"],
            version_name=["v1.0.0"],
        )

        # 結果の検証
        assert isinstance(issue, dict)
        assert issue["issueKey"] == "TEST-1"
        assert issue["summary"] == "名前ベースで更新された課題"
        assert issue["status"]["name"] == "処理中"
        assert issue["assignee"]["name"] == "テストユーザー1"

    def test_update_issue_with_status_id(self, mock_backlog_client: Mock) -> None:
        """ステータスIDを指定して課題を更新するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.update_issue.return_value = {
            "id": 1,
            "issueKey": "TEST-1",
            "summary": "テスト課題1",
            "status": {"id": 3, "name": "処理済み"},
        }

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # ステータスIDを指定して課題を更新
        issue = issue_service.update_issue(issue_id_or_key="TEST-1", status_id=3)

        # モックが呼ばれたことを確認
        mock_backlog_client.update_issue.assert_called_once()
        # 呼び出し時の引数を確認
        args, kwargs = mock_backlog_client.update_issue.call_args
        assert kwargs["issue_id_or_key"] == "TEST-1"
        assert kwargs["status_id"] == 3

        # 結果の検証
        assert isinstance(issue, dict)
        assert issue["status"]["id"] == 3
        assert issue["status"]["name"] == "処理済み"

    def test_update_issue_with_assignee_id(self, mock_backlog_client: Mock) -> None:
        """担当者IDを指定して課題を更新するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.update_issue.return_value = {
            "id": 1,
            "issueKey": "TEST-1",
            "summary": "テスト課題1",
            "assignee": {"id": 456, "name": "新担当者"},
        }

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # 担当者IDを指定して課題を更新
        issue = issue_service.update_issue(issue_id_or_key="TEST-1", assignee_id=456)

        # モックが呼ばれたことを確認
        mock_backlog_client.update_issue.assert_called_once()
        # 呼び出し時の引数を確認
        args, kwargs = mock_backlog_client.update_issue.call_args
        assert kwargs["issue_id_or_key"] == "TEST-1"
        assert kwargs["assignee_id"] == 456

        # 結果の検証
        assert isinstance(issue, dict)
        assert issue["assignee"]["id"] == 456
        assert issue["assignee"]["name"] == "新担当者"

    def test_update_issue_with_dates(self, mock_backlog_client: Mock) -> None:
        """開始日・期限日を指定して課題を更新するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.update_issue.return_value = {
            "id": 1,
            "issueKey": "TEST-1",
            "summary": "テスト課題1",
            "startDate": "2025-05-01",
            "dueDate": "2025-05-31",
        }

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # 開始日・期限日を指定して課題を更新
        issue = issue_service.update_issue(
            issue_id_or_key="TEST-1", start_date="2025-05-01", due_date="2025-05-31"
        )

        # モックが呼ばれたことを確認
        mock_backlog_client.update_issue.assert_called_once()
        # 呼び出し時の引数を確認
        args, kwargs = mock_backlog_client.update_issue.call_args
        assert kwargs["issue_id_or_key"] == "TEST-1"
        assert kwargs["start_date"] == "2025-05-01"
        assert kwargs["due_date"] == "2025-05-31"

        # 結果の検証
        assert isinstance(issue, dict)
        assert issue["startDate"] == "2025-05-01"
        assert issue["dueDate"] == "2025-05-31"

    def test_update_issue_handles_error(self, mock_backlog_client: Mock) -> None:
        """エラー発生時の処理をテスト"""
        # モックがエラーを発生させるように設定
        mock_backlog_client.update_issue.side_effect = Exception("API Error")

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # エラーが発生することを確認
        with pytest.raises(Exception) as excinfo:
            issue_service.update_issue(
                issue_id_or_key="TEST-1", summary="更新された課題"
            )

        # エラーメッセージを確認
        assert "Failed to update issue" in str(excinfo.value)

    def test_delete_issue_returns_true(self, mock_backlog_client: Mock) -> None:
        """課題を削除するメソッドがTrueを返すことを確認するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.delete_issue.return_value = True

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # 課題を削除
        result = issue_service.delete_issue("TEST-1")

        # モックが正しいパラメータで呼ばれたことを確認
        mock_backlog_client.delete_issue.assert_called_once_with("TEST-1")

        # 結果の検証
        assert result is True

    def test_delete_issue_handles_error(self, mock_backlog_client: Mock) -> None:
        """エラー発生時の処理をテスト"""
        # モックがエラーを発生させるように設定
        mock_backlog_client.delete_issue.side_effect = Exception("API Error")

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # エラーが発生することを確認
        with pytest.raises(Exception) as excinfo:
            issue_service.delete_issue("TEST-1")

        # エラーメッセージを確認
        assert "Failed to delete issue" in str(excinfo.value)

    def test_add_comment_returns_dict(self, mock_backlog_client: Mock) -> None:
        """コメントを追加するメソッドが辞書を返すことを確認するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.add_comment.return_value = {
            "id": 1,
            "content": "テストコメント",
        }

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # コメントを追加
        comment = issue_service.add_comment(
            issue_id_or_key="TEST-1", content="テストコメント"
        )

        # モックが正しいパラメータで呼ばれたことを確認
        mock_backlog_client.add_comment.assert_called_once_with(
            issue_id_or_key="TEST-1", content="テストコメント"
        )

        # 結果の検証
        assert isinstance(comment, dict)
        assert comment["id"] == 1
        assert comment["content"] == "テストコメント"

    def test_add_comment_handles_error(self, mock_backlog_client: Mock) -> None:
        """エラー発生時の処理をテスト"""
        # モックがエラーを発生させるように設定
        mock_backlog_client.add_comment.side_effect = Exception("API Error")

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # エラーが発生することを確認
        with pytest.raises(Exception) as excinfo:
            issue_service.add_comment(
                issue_id_or_key="TEST-1", content="テストコメント"
            )

        # エラーメッセージを確認
        assert "Failed to add comment" in str(excinfo.value)

    def test_get_issue_comments_returns_list(self, mock_backlog_client: Mock) -> None:
        """コメント一覧を取得するメソッドがリストを返すことを確認するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.get_issue_comments.return_value = [
            {"id": 1, "content": "コメント1"},
            {"id": 2, "content": "コメント2"},
        ]

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # コメント一覧を取得
        comments = issue_service.get_issue_comments("TEST-1")

        # モックが正しいパラメータで呼ばれたことを確認
        mock_backlog_client.get_issue_comments.assert_called_once_with(
            issue_id_or_key="TEST-1", count=20
        )

        # 結果の検証
        assert isinstance(comments, list)
        assert len(comments) == 2
        assert comments[0]["id"] == 1
        assert comments[0]["content"] == "コメント1"

    def test_get_issue_comments_handles_error(self, mock_backlog_client: Mock) -> None:
        """エラー発生時の処理をテスト"""
        # モックがエラーを発生させるように設定
        mock_backlog_client.get_issue_comments.side_effect = Exception("API Error")

        # テスト対象のサービスをインスタンス化
        issue_service = MockIssueService(backlog_client=mock_backlog_client)

        # エラーが発生することを確認
        with pytest.raises(Exception) as excinfo:
            issue_service.get_issue_comments("TEST-1")

        # エラーメッセージを確認
        assert "Failed to get comments" in str(excinfo.value)
