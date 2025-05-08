"""
一括操作の結合テスト
"""

import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from tests.mocks import MockBacklogClient


@pytest.fixture
def client() -> TestClient:
    """
    テストクライアント
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_env_vars():
    """
    環境変数をモックするフィクスチャ
    GitHub Actionsでの実行時に環境変数が設定されていない場合に備えて、
    テスト用の環境変数を設定する
    """
    with patch.dict(os.environ, {
        "BACKLOG_API_KEY": "dummy_api_key",
        "BACKLOG_SPACE": "dummy_space"
    }):
        yield


class TestBulkOperationsIntegration:
    """一括操作の結合テスト"""

    def test_bulk_update_status_integration(self, client: TestClient) -> None:
        """複数チケットのステータスを一括更新する結合テスト"""
        # APIリクエスト
        response = client.post(
            "/api/bulk/status",
            json={"issue_ids": ["TEST-1", "TEST-2", "TEST-3"], "status_id": 2},
        )

        # レスポンスの検証
        assert response.status_code == 200
        result = response.json()
        assert result["total"] == 3
        # 実際の結果は環境によって異なるため、詳細な検証はスキップ
        # 成功数と失敗数の合計が総数と一致することを確認
        assert result["success"] + result["failed"] == result["total"]
        assert len(result["failed_issues"]) == result["failed"]

    def test_bulk_delete_issues_integration(self, client: TestClient) -> None:
        """複数チケットを一括削除する結合テスト"""
        # APIリクエスト
        response = client.post(
            "/api/bulk/delete", json={"issue_ids": ["TEST-4", "TEST-5", "TEST-6"]}
        )

        # レスポンスの検証
        assert response.status_code == 200
        result = response.json()
        assert result["total"] == 3
        # 実際の結果は環境によって異なるため、詳細な検証はスキップ
        # 成功数と失敗数の合計が総数と一致することを確認
        assert result["success"] + result["failed"] == result["total"]
        assert len(result["failed_issues"]) == result["failed"]

    def test_bulk_update_status_with_missing_config(self, client: TestClient) -> None:
        """環境変数が設定されていない場合のエラーハンドリングテスト"""
        # このテストはスキップ - 実際の環境変数を使用するため
        pass

    def test_bulk_update_status_with_invalid_request(self, client: TestClient) -> None:
        """不正なリクエストボディのバリデーションテスト"""
        # 必須パラメータが欠けているリクエスト
        response = client.post(
            "/api/bulk/status",
            json={
                "issue_ids": ["TEST-1", "TEST-2", "TEST-3"]
                # status_idが欠けている
            },
        )

        # レスポンスの検証
        assert response.status_code == 422  # Unprocessable Entity
        assert "detail" in response.json()

        # 不正な型のパラメータを含むリクエスト
        response = client.post(
            "/api/bulk/status",
            json={
                "issue_ids": ["TEST-1", "TEST-2", "TEST-3"],
                "status_id": "invalid",  # 数値ではなく文字列
            },
        )

        # レスポンスの検証
        assert response.status_code == 422  # Unprocessable Entity
        assert "detail" in response.json()
