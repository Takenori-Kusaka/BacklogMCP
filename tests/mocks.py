"""
テスト用のモックモジュール
"""

from typing import Any, Dict, List, Optional, Union
from unittest.mock import Mock


class MockBacklogClient:
    """
    モックのBacklogクライアント
    """

    def __init__(self, **kwargs) -> None:
        """
        初期化
        """
        pass

    def get_projects(self) -> List[Dict[str, Any]]:
        """
        プロジェクト一覧を取得

        Returns:
            プロジェクト一覧
        """
        return [
            {"id": 1, "projectKey": "TEST1", "name": "テストプロジェクト1"},
            {"id": 2, "projectKey": "TEST2", "name": "テストプロジェクト2"},
        ]

    def get_project(self, project_key: str) -> Dict[str, Any]:
        """
        プロジェクトを取得

        Args:
            project_key: プロジェクトキー

        Returns:
            プロジェクト情報
        """
        return {"id": 1, "projectKey": "TEST1", "name": "テストプロジェクト1"}

    def get_issues(self, **kwargs) -> List[Dict[str, Any]]:
        """
        課題一覧を取得

        Returns:
            課題一覧
        """
        return [
            {"id": 1, "issueKey": "TEST-1", "summary": "テスト課題1"},
            {"id": 2, "issueKey": "TEST-2", "summary": "テスト課題2"},
        ]

    def get_issue(self, issue_id_or_key: str) -> Dict[str, Any]:
        """
        課題情報を取得

        Args:
            issue_id_or_key: 課題IDまたは課題キー

        Returns:
            課題情報
        """
        return {"id": 1, "issueKey": "TEST-1", "summary": "テスト課題1"}

    def get_users(self) -> List[Dict[str, Any]]:
        """
        ユーザー一覧を取得

        Returns:
            ユーザー一覧
        """
        return [
            {"id": 1, "name": "テストユーザー1"},
            {"id": 2, "name": "テストユーザー2"},
        ]

    def get_user_id_by_name(self, user_name: str) -> Optional[int]:
        """
        ユーザー名からユーザーIDを取得

        Args:
            user_name: ユーザー名

        Returns:
            ユーザーID
        """
        users = {"テストユーザー1": 1, "テストユーザー2": 2}
        return users.get(user_name)

    def get_priorities(self) -> List[Dict[str, Any]]:
        """
        優先度一覧を取得

        Returns:
            優先度一覧
        """
        return [
            {"id": 2, "name": "高"},
            {"id": 3, "name": "中"},
            {"id": 4, "name": "低"},
        ]

    def get_priority_id_by_name(self, priority_name: str) -> Optional[int]:
        """
        優先度名から優先度IDを取得

        Args:
            priority_name: 優先度名

        Returns:
            優先度ID
        """
        priorities = {"高": 2, "中": 3, "低": 4}
        return priorities.get(priority_name)

    def get_statuses(self, project_id_or_key: Union[str, int]) -> List[Dict[str, Any]]:
        """
        ステータス一覧を取得

        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー

        Returns:
            ステータス一覧
        """
        return [
            {"id": 1, "name": "未対応"},
            {"id": 2, "name": "処理中"},
            {"id": 3, "name": "処理済み"},
            {"id": 4, "name": "完了"},
        ]

    def get_status_id_by_name(self, project_id_or_key: Union[str, int], status_name: str) -> Optional[int]:
        """
        ステータス名からステータスIDを取得

        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー
            status_name: ステータス名

        Returns:
            ステータスID
        """
        if not status_name:
            return None
        statuses = {"未対応": 1, "処理中": 2, "処理済み": 3, "完了": 4}
        return statuses.get(status_name)

    def get_categories(self, project_id_or_key: Union[str, int]) -> List[Dict[str, Any]]:
        """
        カテゴリー一覧を取得

        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー

        Returns:
            カテゴリー一覧
        """
        return [
            {"id": 1, "name": "フロントエンド"},
            {"id": 2, "name": "バックエンド"},
            {"id": 3, "name": "インフラ"},
        ]

    def get_category_id_by_name(self, project_id_or_key: Union[str, int], category_name: str) -> Optional[int]:
        """
        カテゴリー名からカテゴリーIDを取得

        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー
            category_name: カテゴリー名

        Returns:
            カテゴリーID
        """
        categories = {"フロントエンド": 1, "バックエンド": 2, "インフラ": 3}
        return categories.get(category_name)

    def get_milestones(self, project_id_or_key: Union[str, int]) -> List[Dict[str, Any]]:
        """
        マイルストーン一覧を取得

        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー

        Returns:
            マイルストーン一覧
        """
        return [{"id": 1, "name": "5月リリース"}, {"id": 2, "name": "6月リリース"}]

    def get_milestone_id_by_name(self, project_id_or_key: Union[str, int], milestone_name: str) -> Optional[int]:
        """
        マイルストーン名からマイルストーンIDを取得

        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー
            milestone_name: マイルストーン名

        Returns:
            マイルストーンID
        """
        milestones = {"5月リリース": 1, "6月リリース": 2}
        return milestones.get(milestone_name)

    def get_versions(self, project_id_or_key: Union[str, int]) -> List[Dict[str, Any]]:
        """
        バージョン一覧を取得

        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー

        Returns:
            バージョン一覧
        """
        return [
            {"id": 1, "name": "v1.0.0"},
            {"id": 2, "name": "v1.1.0"},
            {"id": 3, "name": "v1.2.0"},
        ]

    def get_version_id_by_name(self, project_id_or_key: Union[str, int], version_name: str) -> Optional[int]:
        """
        バージョン名からバージョンIDを取得

        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー
            version_name: バージョン名

        Returns:
            バージョンID
        """
        versions = {"v1.0.0": 1, "v1.1.0": 2, "v1.2.0": 3}
        return versions.get(version_name)

    def get_issue_types(self, project_id_or_key: Union[str, int]) -> List[Dict[str, Any]]:
        """
        課題種別一覧を取得

        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー

        Returns:
            課題種別一覧
        """
        return [
            {"id": 1, "name": "タスク"},
            {"id": 2, "name": "バグ"},
            {"id": 3, "name": "要望"},
        ]

    def create_issue(self, **kwargs) -> Dict[str, Any]:
        """
        課題を作成

        Returns:
            作成された課題情報
        """
        # プロジェクトキーからプロジェクトIDを解決
        if kwargs.get("project_id") is None and kwargs.get("project_key") is not None:
            project_key = kwargs.get("project_key")
            if project_key is not None:  # Noneチェックを追加
                project = self.get_project(project_key)
                if project:
                    kwargs["project_id"] = project.get("id")

        # 課題種別名から課題種別IDを解決
        if (
            kwargs.get("issue_type_id") is None
            and kwargs.get("issue_type_name") is not None
        ):
            project_key = kwargs.get("project_key") or "TEST1"
            if project_key is not None:  # Noneチェックを追加
                issue_types = self.get_issue_types(project_key)
                for issue_type in issue_types:
                    if issue_type.get("name") == kwargs.get("issue_type_name"):
                        kwargs["issue_type_id"] = issue_type.get("id")
                        break

        # 優先度名から優先度IDを解決
        if (
            kwargs.get("priority_id") is None
            and kwargs.get("priority_name") is not None
        ):
            priority_name = kwargs.get("priority_name")
            if priority_name is not None:  # Noneチェックを追加
                kwargs["priority_id"] = self.get_priority_id_by_name(priority_name)

        # 担当者名から担当者IDを解決
        if (
            kwargs.get("assignee_id") is None
            and kwargs.get("assignee_name") is not None
        ):
            assignee_name = kwargs.get("assignee_name")
            if assignee_name is not None:  # Noneチェックを追加
                kwargs["assignee_id"] = self.get_user_id_by_name(assignee_name)

        return {
            "id": 1,
            "issueKey": "TEST-1",
            "summary": kwargs.get("summary", "新しい課題"),
        }

    def update_issue(self, issue_id_or_key: str, **kwargs) -> Dict[str, Any]:
        """
        課題を更新

        Args:
            issue_id_or_key: 課題IDまたは課題キー

        Returns:
            更新された課題情報
        """
        # ステータス名からステータスIDを解決
        if kwargs.get("status_id") is None and kwargs.get("status_name") is not None:
            status_name = kwargs.get("status_name")
            if status_name is not None:  # Noneチェックを追加
                kwargs["status_id"] = self.get_status_id_by_name(1, status_name)

        # 優先度名から優先度IDを解決
        if (
            kwargs.get("priority_id") is None
            and kwargs.get("priority_name") is not None
        ):
            priority_name = kwargs.get("priority_name")
            if priority_name is not None:  # Noneチェックを追加
                kwargs["priority_id"] = self.get_priority_id_by_name(priority_name)

        # 担当者名から担当者IDを解決
        if (
            kwargs.get("assignee_id") is None
            and kwargs.get("assignee_name") is not None
        ):
            assignee_name = kwargs.get("assignee_name")
            if assignee_name is not None:  # Noneチェックを追加
                kwargs["assignee_id"] = self.get_user_id_by_name(assignee_name)

        return {
            "id": 1,
            "issueKey": "TEST-1",
            "summary": kwargs.get("summary", "更新された課題"),
        }

    def delete_issue(self, issue_id_or_key: str) -> bool:
        """
        課題を削除

        Args:
            issue_id_or_key: 課題IDまたは課題キー

        Returns:
            削除に成功した場合はTrue
        """
        return True

    def add_comment(self, issue_id_or_key: str, content: str) -> Dict[str, Any]:
        """
        課題にコメントを追加

        Args:
            issue_id_or_key: 課題IDまたは課題キー
            content: コメント内容

        Returns:
            追加されたコメント情報
        """
        return {"id": 1, "content": "テストコメント"}

    def get_issue_comments(self, issue_id_or_key: str, **kwargs) -> List[Dict[str, Any]]:
        """
        課題のコメント一覧を取得

        Args:
            issue_id_or_key: 課題IDまたは課題キー

        Returns:
            コメント一覧
        """
        return [{"id": 1, "content": "コメント1"}, {"id": 2, "content": "コメント2"}]


class MockProjectService:
    """
    モックのプロジェクト管理サービス
    """

    def __init__(self, backlog_client=None) -> None:
        """
        初期化

        Args:
            backlog_client: Backlogクライアント
        """
        self.backlog_client = backlog_client or MockBacklogClient()

    def get_projects(self) -> List[Dict[str, Any]]:
        """
        プロジェクト一覧を取得

        Returns:
            プロジェクト一覧
        """
        return self.backlog_client.get_projects()

    def get_project(self, project_key: str) -> Dict[str, Any]:
        """
        プロジェクトを取得

        Args:
            project_key: プロジェクトキー

        Returns:
            プロジェクト情報
        """
        return self.backlog_client.get_project(project_key)


class MockIssueService:
    """
    モックの課題管理サービス
    """

    def __init__(self, backlog_client=None) -> None:
        """
        初期化

        Args:
            backlog_client: Backlogクライアント
        """
        self.backlog_client = backlog_client or MockBacklogClient()

    def get_issues(
        self, project_id: Optional[int] = None, status_id: Optional[Union[int, List[int]]] = None, 
        assignee_id: Optional[int] = None, keyword: Optional[str] = None, count: int = 20
    ) -> List[Dict[str, Any]]:
        """
        課題一覧を取得

        Args:
            project_id: プロジェクトID
            status_id: ステータスID
            assignee_id: 担当者ID
            keyword: キーワード
            count: 取得件数

        Returns:
            課題一覧
        """
        try:
            return self.backlog_client.get_issues(
                project_id=project_id,
                status_id=status_id,
                assignee_id=assignee_id,
                keyword=keyword,
                count=count,
            )
        except Exception as e:
            raise Exception(f"Failed to get issues: {str(e)}")

    def get_issue(self, issue_id_or_key: str) -> Dict[str, Any]:
        """
        課題情報を取得

        Args:
            issue_id_or_key: 課題IDまたは課題キー

        Returns:
            課題情報
        """
        try:
            return self.backlog_client.get_issue(issue_id_or_key)
        except Exception as e:
            raise Exception(f"Failed to get issue: {str(e)}")

    def create_issue(
        self,
        project_id: Optional[int] = None,
        project_key: Optional[str] = None,
        summary: Optional[str] = None,
        issue_type_id: Optional[int] = None,
        issue_type_name: Optional[str] = None,
        priority_id: Optional[int] = None,
        priority_name: Optional[str] = None,
        description: Optional[str] = None,
        assignee_id: Optional[int] = None,
        assignee_name: Optional[str] = None,
        category_id: Optional[List[int]] = None,
        category_name: Optional[List[str]] = None,
        milestone_id: Optional[List[int]] = None,
        milestone_name: Optional[List[str]] = None,
        version_id: Optional[List[int]] = None,
        version_name: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        課題を作成

        Args:
            project_id: プロジェクトID
            project_key: プロジェクトキー
            summary: 課題名
            issue_type_id: 課題種別ID
            issue_type_name: 課題種別名
            priority_id: 優先度ID
            priority_name: 優先度名
            description: 詳細
            assignee_id: 担当者ID
            assignee_name: 担当者名
            category_id: カテゴリーIDのリスト
            category_name: カテゴリー名のリスト
            milestone_id: マイルストーンIDのリスト
            milestone_name: マイルストーン名のリスト
            version_id: 発生バージョンIDのリスト
            version_name: 発生バージョン名のリスト
            start_date: 開始日
            due_date: 期限日

        Returns:
            作成された課題情報
        """
        try:
            return self.backlog_client.create_issue(
                project_id=project_id,
                project_key=project_key,
                summary=summary,
                issue_type_id=issue_type_id,
                issue_type_name=issue_type_name,
                priority_id=priority_id,
                priority_name=priority_name,
                description=description,
                assignee_id=assignee_id,
                assignee_name=assignee_name,
                category_id=category_id,
                category_name=category_name,
                milestone_id=milestone_id,
                milestone_name=milestone_name,
                version_id=version_id,
                version_name=version_name,
                start_date=start_date,
                due_date=due_date,
            )
        except Exception as e:
            raise Exception(f"Failed to create issue: {str(e)}")

    def update_issue(
        self,
        issue_id_or_key: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        status_id: Optional[int] = None,
        status_name: Optional[str] = None,
        priority_id: Optional[int] = None,
        priority_name: Optional[str] = None,
        assignee_id: Optional[int] = None,
        assignee_name: Optional[str] = None,
        category_id: Optional[List[int]] = None,
        category_name: Optional[List[str]] = None,
        milestone_id: Optional[List[int]] = None,
        milestone_name: Optional[List[str]] = None,
        version_id: Optional[List[int]] = None,
        version_name: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        課題を更新

        Args:
            issue_id_or_key: 課題IDまたは課題キー
            summary: 課題名
            description: 詳細
            status_id: ステータスID
            status_name: ステータス名
            priority_id: 優先度ID
            priority_name: 優先度名
            assignee_id: 担当者ID
            assignee_name: 担当者名
            category_id: カテゴリーIDのリスト
            category_name: カテゴリー名のリスト
            milestone_id: マイルストーンIDのリスト
            milestone_name: マイルストーン名のリスト
            version_id: 発生バージョンIDのリスト
            version_name: 発生バージョン名のリスト
            start_date: 開始日
            due_date: 期限日

        Returns:
            更新された課題情報
        """
        try:
            return self.backlog_client.update_issue(
                issue_id_or_key=issue_id_or_key,
                summary=summary,
                description=description,
                status_id=status_id,
                status_name=status_name,
                priority_id=priority_id,
                priority_name=priority_name,
                assignee_id=assignee_id,
                assignee_name=assignee_name,
                category_id=category_id,
                category_name=category_name,
                milestone_id=milestone_id,
                milestone_name=milestone_name,
                version_id=version_id,
                version_name=version_name,
                start_date=start_date,
                due_date=due_date,
            )
        except Exception as e:
            raise Exception(f"Failed to update issue: {str(e)}")

    def delete_issue(self, issue_id_or_key: str) -> bool:
        """
        課題を削除

        Args:
            issue_id_or_key: 課題IDまたは課題キー

        Returns:
            削除に成功した場合はTrue
        """
        try:
            return self.backlog_client.delete_issue(issue_id_or_key)
        except Exception as e:
            raise Exception(f"Failed to delete issue: {str(e)}")

    def add_comment(self, issue_id_or_key: str, content: str) -> Dict[str, Any]:
        """
        課題にコメントを追加

        Args:
            issue_id_or_key: 課題IDまたは課題キー
            content: コメント内容

        Returns:
            追加されたコメント情報
        """
        try:
            return self.backlog_client.add_comment(
                issue_id_or_key=issue_id_or_key, content=content
            )
        except Exception as e:
            raise Exception(f"Failed to add comment: {str(e)}")

    def get_issue_comments(self, issue_id_or_key: str, count: int = 20) -> List[Dict[str, Any]]:
        """
        課題のコメント一覧を取得

        Args:
            issue_id_or_key: 課題IDまたは課題キー
            count: 取得件数

        Returns:
            コメント一覧
        """
        try:
            return self.backlog_client.get_issue_comments(
                issue_id_or_key=issue_id_or_key, count=count
            )
        except Exception as e:
            raise Exception(f"Failed to get comments: {str(e)}")

    def get_issue_types(self, project_key: Union[str, int]) -> List[Dict[str, Any]]:
        """
        課題種別一覧を取得

        Args:
            project_key: プロジェクトキー

        Returns:
            課題種別一覧
        """
        try:
            return self.backlog_client.get_issue_types(project_key)
        except Exception as e:
            raise Exception(f"Failed to get issue types: {str(e)}")
