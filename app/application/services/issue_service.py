"""
課題管理サービス
"""

from typing import Any, Dict, List, Optional, Union

from app.infrastructure.backlog.backlog_client_wrapper import BacklogClientWrapper


class IssueService:
    """
    課題管理サービス

    課題関連の業務ロジックを実装するサービスクラス
    """

    def __init__(self, backlog_client: BacklogClientWrapper):
        """
        初期化

        Args:
            backlog_client: Backlogクライアント
        """
        self.backlog_client = backlog_client

    def get_issues(
        self,
        project_id: Optional[int] = None,
        status_id: Optional[List[int]] = None,
        assignee_id: Optional[int] = None,
        keyword: Optional[str] = None,
        count: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        課題一覧を取得

        Args:
            project_id: プロジェクトID（指定しない場合は全プロジェクト）
            status_id: ステータスID（指定しない場合は全ステータス）
            assignee_id: 担当者ID（指定しない場合は全担当者）
            keyword: 検索キーワード
            count: 取得件数（デフォルト20件）

        Returns:
            課題一覧

        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            issues = self.backlog_client.get_issues(
                project_id=project_id,
                status_id=status_id,
                assignee_id=assignee_id,
                keyword=keyword,
                count=count,
            )
            return issues
        except Exception as e:
            # エラーログの出力など
            print(f"Error getting issues: {e}")
            # 呼び出し元でハンドリングできるように例外を再スロー
            raise Exception(f"Failed to get issues: {e}") from e

    def get_issue(self, issue_id_or_key: str) -> Optional[Dict[str, Any]]:
        """
        課題情報を取得

        Args:
            issue_id_or_key: 課題IDまたは課題キー

        Returns:
            課題情報。課題が存在しない場合はNone

        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            issue = self.backlog_client.get_issue(issue_id_or_key)
            return issue
        except Exception as e:
            # エラーログの出力など
            print(f"Error getting issue {issue_id_or_key}: {e}")
            # 呼び出し元でハンドリングできるように例外を再スロー
            raise Exception(f"Failed to get issue {issue_id_or_key}: {e}") from e

    def create_issue(
        self,
        project_id: Optional[int] = None,
        project_key: Optional[str] = None,
        summary: str = "",
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
            project_key: プロジェクトキー（project_idが指定されていない場合に使用）
            summary: 課題の件名
            issue_type_id: 課題の種別ID
            issue_type_name: 課題の種別名（issue_type_idが指定されていない場合に使用）
            priority_id: 優先度ID
            priority_name: 優先度名（priority_idが指定されていない場合に使用）
            description: 課題の詳細
            assignee_id: 担当者ID
            assignee_name: 担当者名（assignee_idが指定されていない場合に使用）
            category_id: カテゴリーIDのリスト
            category_name: カテゴリー名のリスト（category_idが指定されていない場合に使用）
            milestone_id: マイルストーンIDのリスト
            milestone_name: マイルストーン名のリスト（milestone_idが指定されていない場合に使用）
            version_id: 発生バージョンIDのリスト
            version_name: 発生バージョン名のリスト（version_idが指定されていない場合に使用）
            start_date: 開始日（yyyy-MM-dd形式）
            due_date: 期限日（yyyy-MM-dd形式）

        Returns:
            作成された課題情報

        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            issue = self.backlog_client.create_issue(
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
            if issue is None:
                raise Exception("Failed to create issue")
            return issue
        except Exception as e:
            # エラーログの出力など
            print(f"Error creating issue: {e}")
            # 呼び出し元でハンドリングできるように例外を再スロー
            raise Exception(f"Failed to create issue: {e}") from e

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
            summary: 課題の件名
            description: 課題の詳細
            status_id: ステータスID
            status_name: ステータス名（status_idが指定されていない場合に使用）
            priority_id: 優先度ID
            priority_name: 優先度名（priority_idが指定されていない場合に使用）
            assignee_id: 担当者ID
            assignee_name: 担当者名（assignee_idが指定されていない場合に使用）
            category_id: カテゴリーIDのリスト
            category_name: カテゴリー名のリスト（category_idが指定されていない場合に使用）
            milestone_id: マイルストーンIDのリスト
            milestone_name: マイルストーン名のリスト（milestone_idが指定されていない場合に使用）
            version_id: 発生バージョンIDのリスト
            version_name: 発生バージョン名のリスト（version_idが指定されていない場合に使用）
            start_date: 開始日（yyyy-MM-dd形式）
            due_date: 期限日（yyyy-MM-dd形式）

        Returns:
            更新された課題情報

        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            issue = self.backlog_client.update_issue(
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
            if issue is None:
                raise Exception(f"Failed to update issue {issue_id_or_key}")
            return issue
        except Exception as e:
            # エラーログの出力など
            print(f"Error updating issue {issue_id_or_key}: {e}")
            # 呼び出し元でハンドリングできるように例外を再スロー
            raise Exception(f"Failed to update issue {issue_id_or_key}: {e}") from e

    def delete_issue(self, issue_id_or_key: str) -> bool:
        """
        課題を削除

        Args:
            issue_id_or_key: 課題IDまたは課題キー

        Returns:
            削除に成功した場合はTrue

        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            result = self.backlog_client.delete_issue(issue_id_or_key)
            if not result:
                raise Exception(f"Failed to delete issue {issue_id_or_key}")
            return True
        except Exception as e:
            # エラーログの出力など
            print(f"Error deleting issue {issue_id_or_key}: {e}")
            # 呼び出し元でハンドリングできるように例外を再スロー
            raise Exception(f"Failed to delete issue {issue_id_or_key}: {e}") from e

    def add_comment(self, issue_id_or_key: str, content: str) -> Dict[str, Any]:
        """
        課題にコメントを追加

        Args:
            issue_id_or_key: 課題IDまたは課題キー
            content: コメント内容

        Returns:
            追加されたコメント情報

        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            comment = self.backlog_client.add_comment(
                issue_id_or_key=issue_id_or_key, content=content
            )
            if comment is None:
                raise Exception(f"Failed to add comment to issue {issue_id_or_key}")
            return comment
        except Exception as e:
            # エラーログの出力など
            print(f"Error adding comment to issue {issue_id_or_key}: {e}")
            # 呼び出し元でハンドリングできるように例外を再スロー
            raise Exception(
                f"Failed to add comment to issue {issue_id_or_key}: {e}"
            ) from e

    def get_issue_comments(
        self, issue_id_or_key: str, count: int = 20
    ) -> List[Dict[str, Any]]:
        """
        課題のコメント一覧を取得

        Args:
            issue_id_or_key: 課題IDまたは課題キー
            count: 取得件数（デフォルト20件）

        Returns:
            コメント一覧

        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            comments = self.backlog_client.get_issue_comments(
                issue_id_or_key=issue_id_or_key, count=count
            )
            return comments
        except Exception as e:
            # エラーログの出力など
            print(f"Error getting comments for issue {issue_id_or_key}: {e}")
            # 呼び出し元でハンドリングできるように例外を再スロー
            raise Exception(
                f"Failed to get comments for issue {issue_id_or_key}: {e}"
            ) from e

    def get_issue_types(
        self, project_id_or_key: Union[str, int]
    ) -> List[Dict[str, Any]]:
        """
        課題の種別一覧を取得

        Args:
            project_id_or_key: プロジェクトIDまたはプロジェクトキー

        Returns:
            課題の種別一覧

        Raises:
            Exception: API呼び出しに失敗した場合
        """
        try:
            issue_types = self.backlog_client.get_issue_types(project_id_or_key)
            return issue_types
        except Exception as e:
            # エラーログの出力など
            print(f"Error getting issue types for project {project_id_or_key}: {e}")
            # 呼び出し元でハンドリングできるように例外を再スロー
            raise Exception(
                f"Failed to get issue types for project {project_id_or_key}: {e}"
            ) from e
