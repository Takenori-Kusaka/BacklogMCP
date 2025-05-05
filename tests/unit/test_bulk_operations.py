"""
一括操作のユニットテスト
"""
import pytest
from unittest.mock import Mock, patch
from app.application.services.bulk_operations_service import BulkOperationsService


class TestBulkOperationsService:
    """一括操作サービスのテストクラス"""
    
    def test_bulk_update_status_returns_success_count(self, mock_backlog_client):
        """複数チケットのステータスを一括更新するメソッドが成功件数を返すことを確認するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.update_issue.side_effect = [
            {"id": 1, "issueKey": "TEST-1", "status": {"id": 2, "name": "処理中"}},
            {"id": 2, "issueKey": "TEST-2", "status": {"id": 2, "name": "処理中"}},
            Exception("API Error")  # 3つ目は失敗するケース
        ]
        
        # テスト対象のサービスをインスタンス化
        bulk_service = BulkOperationsService(backlog_client=mock_backlog_client)
        
        # 複数チケットのステータスを一括更新
        result = bulk_service.bulk_update_status(
            issue_ids=["TEST-1", "TEST-2", "TEST-3"],
            status_id=2
        )
        
        # モックが正しいパラメータで呼ばれたことを確認
        assert mock_backlog_client.update_issue.call_count == 3
        mock_backlog_client.update_issue.assert_any_call(
            issue_id_or_key="TEST-1",
            status_id=2
        )
        mock_backlog_client.update_issue.assert_any_call(
            issue_id_or_key="TEST-2",
            status_id=2
        )
        mock_backlog_client.update_issue.assert_any_call(
            issue_id_or_key="TEST-3",
            status_id=2
        )
        
        # 結果の検証
        assert result["total"] == 3
        assert result["success"] == 2
        assert result["failed"] == 1
        assert len(result["failed_issues"]) == 1
        assert result["failed_issues"][0] == "TEST-3"
    
    def test_bulk_update_assignee_returns_success_count(self, mock_backlog_client):
        """複数チケットの担当者を一括更新するメソッドが成功件数を返すことを確認するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.update_issue.side_effect = [
            {"id": 1, "issueKey": "TEST-1", "assignee": {"id": 123, "name": "テストユーザー"}},
            {"id": 2, "issueKey": "TEST-2", "assignee": {"id": 123, "name": "テストユーザー"}}
        ]
        
        # テスト対象のサービスをインスタンス化
        bulk_service = BulkOperationsService(backlog_client=mock_backlog_client)
        
        # 複数チケットの担当者を一括更新
        result = bulk_service.bulk_update_assignee(
            issue_ids=["TEST-1", "TEST-2"],
            assignee_id=123
        )
        
        # モックが正しいパラメータで呼ばれたことを確認
        assert mock_backlog_client.update_issue.call_count == 2
        mock_backlog_client.update_issue.assert_any_call(
            issue_id_or_key="TEST-1",
            assignee_id=123
        )
        mock_backlog_client.update_issue.assert_any_call(
            issue_id_or_key="TEST-2",
            assignee_id=123
        )
        
        # 結果の検証
        assert result["total"] == 2
        assert result["success"] == 2
        assert result["failed"] == 0
        assert len(result["failed_issues"]) == 0
    
    def test_bulk_update_priority_returns_success_count(self, mock_backlog_client):
        """複数チケットの優先度を一括更新するメソッドが成功件数を返すことを確認するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.update_issue.side_effect = [
            {"id": 1, "issueKey": "TEST-1", "priority": {"id": 3, "name": "中"}},
            Exception("API Error")  # 2つ目は失敗するケース
        ]
        
        # テスト対象のサービスをインスタンス化
        bulk_service = BulkOperationsService(backlog_client=mock_backlog_client)
        
        # 複数チケットの優先度を一括更新
        result = bulk_service.bulk_update_priority(
            issue_ids=["TEST-1", "TEST-2"],
            priority_id=3
        )
        
        # モックが正しいパラメータで呼ばれたことを確認
        assert mock_backlog_client.update_issue.call_count == 2
        mock_backlog_client.update_issue.assert_any_call(
            issue_id_or_key="TEST-1",
            priority_id=3
        )
        mock_backlog_client.update_issue.assert_any_call(
            issue_id_or_key="TEST-2",
            priority_id=3
        )
        
        # 結果の検証
        assert result["total"] == 2
        assert result["success"] == 1
        assert result["failed"] == 1
        assert len(result["failed_issues"]) == 1
        assert result["failed_issues"][0] == "TEST-2"
    
    def test_bulk_update_milestone_returns_success_count(self, mock_backlog_client):
        """複数チケットのマイルストーンを一括更新するメソッドが成功件数を返すことを確認するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.update_issue.side_effect = [
            {"id": 1, "issueKey": "TEST-1", "milestone": [{"id": 5, "name": "リリース1.0"}]},
            {"id": 2, "issueKey": "TEST-2", "milestone": [{"id": 5, "name": "リリース1.0"}]}
        ]
        
        # テスト対象のサービスをインスタンス化
        bulk_service = BulkOperationsService(backlog_client=mock_backlog_client)
        
        # 複数チケットのマイルストーンを一括更新
        result = bulk_service.bulk_update_milestone(
            issue_ids=["TEST-1", "TEST-2"],
            milestone_id=5
        )
        
        # モックが正しいパラメータで呼ばれたことを確認
        assert mock_backlog_client.update_issue.call_count == 2
        mock_backlog_client.update_issue.assert_any_call(
            issue_id_or_key="TEST-1",
            milestone_id=[5]
        )
        mock_backlog_client.update_issue.assert_any_call(
            issue_id_or_key="TEST-2",
            milestone_id=[5]
        )
        
        # 結果の検証
        assert result["total"] == 2
        assert result["success"] == 2
        assert result["failed"] == 0
        assert len(result["failed_issues"]) == 0
    
    def test_bulk_update_category_returns_success_count(self, mock_backlog_client):
        """複数チケットのカテゴリを一括更新するメソッドが成功件数を返すことを確認するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.update_issue.side_effect = [
            {"id": 1, "issueKey": "TEST-1", "category": [{"id": 10, "name": "バグ"}]},
            {"id": 2, "issueKey": "TEST-2", "category": [{"id": 10, "name": "バグ"}]}
        ]
        
        # テスト対象のサービスをインスタンス化
        bulk_service = BulkOperationsService(backlog_client=mock_backlog_client)
        
        # 複数チケットのカテゴリを一括更新
        result = bulk_service.bulk_update_category(
            issue_ids=["TEST-1", "TEST-2"],
            category_id=10
        )
        
        # モックが正しいパラメータで呼ばれたことを確認
        assert mock_backlog_client.update_issue.call_count == 2
        mock_backlog_client.update_issue.assert_any_call(
            issue_id_or_key="TEST-1",
            category_id=[10]
        )
        mock_backlog_client.update_issue.assert_any_call(
            issue_id_or_key="TEST-2",
            category_id=[10]
        )
        
        # 結果の検証
        assert result["total"] == 2
        assert result["success"] == 2
        assert result["failed"] == 0
        assert len(result["failed_issues"]) == 0
    
    def test_bulk_delete_issues_returns_success_count(self, mock_backlog_client):
        """複数チケットを一括削除するメソッドが成功件数を返すことを確認するテスト"""
        # モックの戻り値を設定
        mock_backlog_client.delete_issue.side_effect = [
            True,
            False,
            Exception("API Error")  # 3つ目は例外を発生させる
        ]
        
        # テスト対象のサービスをインスタンス化
        bulk_service = BulkOperationsService(backlog_client=mock_backlog_client)
        
        # 複数チケットを一括削除
        result = bulk_service.bulk_delete_issues(
            issue_ids=["TEST-1", "TEST-2", "TEST-3"]
        )
        
        # モックが正しいパラメータで呼ばれたことを確認
        assert mock_backlog_client.delete_issue.call_count == 3
        mock_backlog_client.delete_issue.assert_any_call("TEST-1")
        mock_backlog_client.delete_issue.assert_any_call("TEST-2")
        mock_backlog_client.delete_issue.assert_any_call("TEST-3")
        
        # 結果の検証
        assert result["total"] == 3
        assert result["success"] == 1
        assert result["failed"] == 2
        assert len(result["failed_issues"]) == 2
        assert "TEST-2" in result["failed_issues"]
        assert "TEST-3" in result["failed_issues"]
