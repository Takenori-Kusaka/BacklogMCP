"""
一括操作サービス
"""

from typing import Any, Dict, List, Optional

from app.infrastructure.backlog.backlog_client_wrapper import BacklogClientWrapper


class BulkOperationsService:
    """
    一括操作サービス

    複数のチケットに対して一括で操作を行うサービスクラス
    """

    def __init__(self, backlog_client: BacklogClientWrapper):
        """
        初期化

        Args:
            backlog_client: Backlogクライアント
        """
        self.backlog_client = backlog_client

    def bulk_update_status(
        self, issue_ids: List[str], status_id: int
    ) -> Dict[str, Any]:
        """
        複数チケットのステータスを一括更新

        Args:
            issue_ids: 課題IDまたは課題キーのリスト
            status_id: 更新後のステータスID

        Returns:
            処理結果の統計情報
            {
                "total": 処理対象の総数,
                "success": 成功した件数,
                "failed": 失敗した件数,
                "failed_issues": 失敗した課題IDまたは課題キーのリスト
            }
        """
        total = len(issue_ids)
        success = 0
        failed_issues = []

        for issue_id in issue_ids:
            try:
                result = self.backlog_client.update_issue(
                    issue_id_or_key=issue_id, status_id=status_id
                )
                if result:
                    success += 1
                else:
                    failed_issues.append(issue_id)
            except Exception as e:
                # エラーログの出力など
                print(f"Error updating status for issue {issue_id}: {e}")
                failed_issues.append(issue_id)

        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "failed_issues": failed_issues,
        }

    def bulk_update_assignee(
        self, issue_ids: List[str], assignee_id: int
    ) -> Dict[str, Any]:
        """
        複数チケットの担当者を一括更新

        Args:
            issue_ids: 課題IDまたは課題キーのリスト
            assignee_id: 更新後の担当者ID

        Returns:
            処理結果の統計情報
            {
                "total": 処理対象の総数,
                "success": 成功した件数,
                "failed": 失敗した件数,
                "failed_issues": 失敗した課題IDまたは課題キーのリスト
            }
        """
        total = len(issue_ids)
        success = 0
        failed_issues = []

        for issue_id in issue_ids:
            try:
                result = self.backlog_client.update_issue(
                    issue_id_or_key=issue_id, assignee_id=assignee_id
                )
                if result:
                    success += 1
                else:
                    failed_issues.append(issue_id)
            except Exception as e:
                # エラーログの出力など
                print(f"Error updating assignee for issue {issue_id}: {e}")
                failed_issues.append(issue_id)

        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "failed_issues": failed_issues,
        }

    def bulk_update_priority(
        self, issue_ids: List[str], priority_id: int
    ) -> Dict[str, Any]:
        """
        複数チケットの優先度を一括更新

        Args:
            issue_ids: 課題IDまたは課題キーのリスト
            priority_id: 更新後の優先度ID

        Returns:
            処理結果の統計情報
            {
                "total": 処理対象の総数,
                "success": 成功した件数,
                "failed": 失敗した件数,
                "failed_issues": 失敗した課題IDまたは課題キーのリスト
            }
        """
        total = len(issue_ids)
        success = 0
        failed_issues = []

        for issue_id in issue_ids:
            try:
                result = self.backlog_client.update_issue(
                    issue_id_or_key=issue_id, priority_id=priority_id
                )
                if result:
                    success += 1
                else:
                    failed_issues.append(issue_id)
            except Exception as e:
                # エラーログの出力など
                print(f"Error updating priority for issue {issue_id}: {e}")
                failed_issues.append(issue_id)

        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "failed_issues": failed_issues,
        }

    def bulk_update_milestone(
        self, issue_ids: List[str], milestone_id: int
    ) -> Dict[str, Any]:
        """
        複数チケットのマイルストーンを一括更新

        Args:
            issue_ids: 課題IDまたは課題キーのリスト
            milestone_id: 更新後のマイルストーンID

        Returns:
            処理結果の統計情報
            {
                "total": 処理対象の総数,
                "success": 成功した件数,
                "failed": 失敗した件数,
                "failed_issues": 失敗した課題IDまたは課題キーのリスト
            }
        """
        total = len(issue_ids)
        success = 0
        failed_issues = []

        for issue_id in issue_ids:
            try:
                # マイルストーンIDはリストで指定する必要がある
                result = self.backlog_client.update_issue(
                    issue_id_or_key=issue_id, milestone_id=[milestone_id]
                )
                if result:
                    success += 1
                else:
                    failed_issues.append(issue_id)
            except Exception as e:
                # エラーログの出力など
                print(f"Error updating milestone for issue {issue_id}: {e}")
                failed_issues.append(issue_id)

        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "failed_issues": failed_issues,
        }

    def bulk_update_category(
        self, issue_ids: List[str], category_id: int
    ) -> Dict[str, Any]:
        """
        複数チケットのカテゴリを一括更新

        Args:
            issue_ids: 課題IDまたは課題キーのリスト
            category_id: 更新後のカテゴリID

        Returns:
            処理結果の統計情報
            {
                "total": 処理対象の総数,
                "success": 成功した件数,
                "failed": 失敗した件数,
                "failed_issues": 失敗した課題IDまたは課題キーのリスト
            }
        """
        total = len(issue_ids)
        success = 0
        failed_issues = []

        for issue_id in issue_ids:
            try:
                # カテゴリIDはリストで指定する必要がある
                result = self.backlog_client.update_issue(
                    issue_id_or_key=issue_id, category_id=[category_id]
                )
                if result:
                    success += 1
                else:
                    failed_issues.append(issue_id)
            except Exception as e:
                # エラーログの出力など
                print(f"Error updating category for issue {issue_id}: {e}")
                failed_issues.append(issue_id)

        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "failed_issues": failed_issues,
        }

    def bulk_delete_issues(self, issue_ids: List[str]) -> Dict[str, Any]:
        """
        複数チケットを一括削除

        Args:
            issue_ids: 課題IDまたは課題キーのリスト

        Returns:
            処理結果の統計情報
            {
                "total": 処理対象の総数,
                "success": 成功した件数,
                "failed": 失敗した件数,
                "failed_issues": 失敗した課題IDまたは課題キーのリスト
            }
        """
        total = len(issue_ids)
        success = 0
        failed_issues = []

        for issue_id in issue_ids:
            try:
                result = self.backlog_client.delete_issue(issue_id)
                if result:
                    success += 1
                else:
                    failed_issues.append(issue_id)
            except Exception as e:
                # エラーログの出力など
                print(f"Error deleting issue {issue_id}: {e}")
                failed_issues.append(issue_id)

        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "failed_issues": failed_issues,
        }
