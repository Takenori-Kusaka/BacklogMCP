"""
BacklogMCPバルク操作の同期的なエンドツーエンドテスト
"""

import os
import pytest
from tests.e2e.sync_test_utils import SyncMCPClient, log_step
from tests.logger_config import setup_logger

# テスト用のロガー
logger = setup_logger("test_bulk_operations_sync_e2e", "test_bulk_operations_sync_e2e.log")


def test_bulk_update_status_e2e(mcp_server_url: str) -> None:
    """FastAPIサーバー経由で複数チケットのステータスを一括更新する同期的なE2Eテスト"""
    # テスト開始をログに記録
    log_step("テスト開始: test_bulk_update_status_e2e")
    
    # 環境変数のチェック
    if not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE"):
        pytest.skip("Backlog API環境変数が設定されていません")
    
    # 同期的なMCPクライアントを使用
    with SyncMCPClient(mcp_server_url, timeout=5) as client:
        # 一括ステータス更新
        log_step("複数チケットのステータスを一括更新")
        try:
            result = client.get_json_result(
                "bulk_update_status",
                {"issue_ids": ["TEST-1", "TEST-2", "TEST-3"], "status_id": 2}
            )
            
            # 結果の検証
            assert "total" in result
            assert "success" in result
            assert "failed" in result
            assert "failed_issues" in result
            
            log_step(f"一括更新結果: 合計={result['total']}, 成功={result['success']}, 失敗={result['failed']}")
            assert result["success"] + result["failed"] == result["total"]
            assert len(result["failed_issues"]) == result["failed"]
            
            # 失敗したチケットがある場合は詳細を表示
            if result["failed"] > 0:
                log_step(f"失敗したチケットID: {', '.join(result['failed_issues'])}")
        except Exception as e:
            log_step(f"エラーが発生しました: {str(e)}")
            raise
    
    # テスト終了をログに記録
    log_step("テスト終了: test_bulk_update_status_e2e")


def test_bulk_delete_issues_e2e(mcp_server_url: str) -> None:
    """FastAPIサーバー経由で複数チケットを一括削除する同期的なE2Eテスト"""
    # テスト開始をログに記録
    log_step("テスト開始: test_bulk_delete_issues_e2e")
    
    # 環境変数のチェック
    if not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE"):
        pytest.skip("Backlog API環境変数が設定されていません")
    
    # 同期的なMCPクライアントを使用
    with SyncMCPClient(mcp_server_url, timeout=5) as client:
        # 一括削除
        log_step("複数チケットを一括削除")
        try:
            result = client.get_json_result(
                "bulk_delete_issues", 
                {"issue_ids": ["TEST-4", "TEST-5", "TEST-6"]}
            )
            
            # 結果の検証
            assert "total" in result
            assert "success" in result
            assert "failed" in result
            assert "failed_issues" in result
            
            log_step(f"一括削除結果: 合計={result['total']}, 成功={result['success']}, 失敗={result['failed']}")
            assert result["success"] + result["failed"] == result["total"]
            assert len(result["failed_issues"]) == result["failed"]
            
            # 失敗したチケットがある場合は詳細を表示
            if result["failed"] > 0:
                for failed_issue in result["failed_issues"]:
                    log_step(f"削除失敗: {failed_issue['issue_id']} - {failed_issue['error']}")
        except Exception as e:
            log_step(f"エラーが発生しました: {str(e)}")
            raise
    
    # テスト終了をログに記録
    log_step("テスト終了: test_bulk_delete_issues_e2e")


def test_bulk_update_status_with_invalid_request(mcp_server_url: str) -> None:
    """FastAPIサーバー経由で不正なリクエストボディのバリデーションテスト（同期版）"""
    # テスト開始をログに記録
    log_step("テスト開始: test_bulk_update_status_with_invalid_request")
    
    # 同期的なMCPクライアントを使用
    with SyncMCPClient(mcp_server_url, timeout=5) as client:
        # 必須パラメータが欠けている
        log_step("必須パラメータが欠けているリクエストを送信")
        try:
            client.get_json_result(
                "bulk_update_status",
                {
                    "issue_ids": ["TEST-1", "TEST-2", "TEST-3"]
                }  # status_idが欠けている
            )
            # 例外が発生するはずなので、ここに到達したらテスト失敗
            log_step("エラーが発生しませんでした（テスト失敗）")
            assert False, "必須パラメータが欠けているのに例外が発生しませんでした"
        except Exception as e:
            # エラーが発生することを確認
            log_step(f"期待通りのエラーが発生: {str(e)}")
            assert "status_id" in str(e).lower() or "required" in str(e).lower()
        
        # 不正な型のパラメータ
        log_step("不正な型のパラメータを含むリクエストを送信")
        try:
            client.get_json_result(
                "bulk_update_status",
                {
                    "issue_ids": ["TEST-1", "TEST-2", "TEST-3"],
                    "status_id": "invalid"  # 数値ではなく文字列
                }
            )
            # 例外が発生するはずなので、ここに到達したらテスト失敗
            log_step("エラーが発生しませんでした（テスト失敗）")
            assert False, "不正な型のパラメータなのに例外が発生しませんでした"
        except Exception as e:
            # エラーが発生することを確認
            log_step(f"期待通りのエラーが発生: {str(e)}")
            assert "status_id" in str(e).lower() or "type" in str(e).lower()
    
    # テスト終了をログに記録
    log_step("テスト終了: test_bulk_update_status_with_invalid_request")


def test_bulk_update_assignee_e2e(mcp_server_url: str) -> None:
    """FastAPIサーバー経由で複数チケットの担当者を一括更新する同期的なE2Eテスト"""
    # テスト開始をログに記録
    log_step("テスト開始: test_bulk_update_assignee_e2e")
    
    # 環境変数のチェック
    if not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE"):
        pytest.skip("Backlog API環境変数が設定されていません")
    
    # 同期的なMCPクライアントを使用
    with SyncMCPClient(mcp_server_url, timeout=5) as client:
        # 一括担当者更新
        log_step("複数チケットの担当者を一括更新")
        try:
            result = client.get_json_result(
                "bulk_update_assignee",
                {"issue_ids": ["TEST-1", "TEST-2", "TEST-3"], "assignee_id": 1}
            )
            
            # 結果の検証
            assert "total" in result
            assert "success" in result
            assert "failed" in result
            assert "failed_issues" in result
            
            log_step(f"一括担当者更新結果: 合計={result['total']}, 成功={result['success']}, 失敗={result['failed']}")
            assert result["success"] + result["failed"] == result["total"]
            assert len(result["failed_issues"]) == result["failed"]
            
            # 失敗したチケットがある場合は詳細を表示
            if result["failed"] > 0:
                for failed_issue in result["failed_issues"]:
                    log_step(f"更新失敗: {failed_issue['issue_id']} - {failed_issue['error']}")
        except Exception as e:
            log_step(f"エラーが発生しました: {str(e)}")
            raise
    
    # テスト終了をログに記録
    log_step("テスト終了: test_bulk_update_assignee_e2e")


def test_bulk_update_category_e2e(mcp_server_url: str) -> None:
    """FastAPIサーバー経由で複数チケットのカテゴリを一括更新する同期的なE2Eテスト"""
    # テスト開始をログに記録
    log_step("テスト開始: test_bulk_update_category_e2e")
    
    # 環境変数のチェック
    if not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE"):
        pytest.skip("Backlog API環境変数が設定されていません")
    
    # 同期的なMCPクライアントを使用
    with SyncMCPClient(mcp_server_url, timeout=5) as client:
        # SyncMCPClient のインスタンス化とクリーンアップがエラーなく行えることを確認する
        log_step("SyncMCPClient のインスタンス化とコンテキスト管理のテスト")
        assert client is not None, "SyncMCPClient のインスタンス化に失敗しました"
        log_step("SyncMCPClient のインスタンス化成功")

        # 一括カテゴリ更新
        log_step("複数チケットのカテゴリを一括更新")
        try:
            result = client.get_json_result(
                "bulk_update_category",
                {"issue_ids": ["TEST-1", "TEST-2", "TEST-3"], "category_ids": [1, 2]}
            )
            
            # 結果の検証
            assert "total" in result
            assert "success" in result
            assert "failed" in result
            assert "failed_issues" in result
            
            log_step(f"一括カテゴリ更新結果: 合計={result['total']}, 成功={result['success']}, 失敗={result['failed']}")
            assert result["success"] + result["failed"] == result["total"]
            assert len(result["failed_issues"]) == result["failed"]
            
            # 失敗したチケットがある場合は詳細を表示
            if result["failed"] > 0:
                for failed_issue in result["failed_issues"]:
                    log_step(f"更新失敗: {failed_issue['issue_id']} - {failed_issue['error']}")
        except Exception as e:
            log_step(f"エラーが発生しました: {str(e)}")
            raise
    
    # テスト終了をログに記録
    log_step("テスト終了: test_bulk_update_category_e2e")
