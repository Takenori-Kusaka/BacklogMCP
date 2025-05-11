"""
プロジェクト管理APIの直接呼び出しテスト
"""

import os

import pytest
import requests

from tests.logger_config import setup_logger

# テスト用のロガー
logger = setup_logger("test_project_api_direct", "test_project_api_direct.log")


@pytest.mark.skipif(
    not os.getenv("DEPLOYED_API_ENDPOINT") or not os.getenv("DEPLOYED_API_KEY"),
    reason="デプロイ済みAPIの環境変数 (DEPLOYED_API_ENDPOINT, DEPLOYED_API_KEY) が設定されていません",
)
def test_get_projects_direct() -> None:
    """APIエンドポイントを直接呼び出してプロジェクト一覧を取得するテスト"""
    logger.info(f"テスト開始: test_get_projects_direct")

    api_endpoint = os.getenv("DEPLOYED_API_ENDPOINT")
    api_key = os.getenv("DEPLOYED_API_KEY")

    # APIエンドポイントを直接呼び出す
    api_url = f"{api_endpoint}/api/v1/projects/" # v1を追加
    logger.info(f"API URL: {api_url}")
    headers = {"x-api-key": api_key}
    logger.info(f"Headers: {{'x-api-key': '********'}}") # APIキーはログに出力しない

    try:
        response = requests.get(api_url, headers=headers)
        logger.info(f"ステータスコード: {response.status_code}")
        logger.info(f"レスポンス: {response.text}")

        # レスポンスの検証
        assert response.status_code == 200
        projects = response.json()
        assert isinstance(projects, list)
        if projects:
            assert "projectKey" in projects[0]
            assert "name" in projects[0]

        logger.info(f"テスト完了: test_get_projects_direct")
    except Exception as e:
        logger.error(f"テスト失敗: {str(e)}")
        raise


@pytest.mark.skipif(
    not os.getenv("DEPLOYED_API_ENDPOINT")
    or not os.getenv("DEPLOYED_API_KEY")
    or not os.getenv("BACKLOG_PROJECT"), # BACKLOG_PROJECTは引き続き利用
    reason="デプロイ済みAPIの環境変数 (DEPLOYED_API_ENDPOINT, DEPLOYED_API_KEY) または BACKLOG_PROJECT が設定されていません",
)
def test_get_project_by_key_direct() -> None:
    """APIエンドポイントを直接呼び出して特定プロジェクトを取得するテスト"""
    logger.info(f"テスト開始: test_get_project_by_key_direct")

    api_endpoint = os.getenv("DEPLOYED_API_ENDPOINT")
    api_key = os.getenv("DEPLOYED_API_KEY")
    project_key = os.getenv("BACKLOG_PROJECT")
    logger.info(f"プロジェクトキー: {project_key}")

    # APIエンドポイントを直接呼び出す
    api_url = f"{api_endpoint}/api/v1/projects/{project_key}" # v1を追加
    logger.info(f"API URL: {api_url}")
    headers = {"x-api-key": api_key}
    logger.info(f"Headers: {{'x-api-key': '********'}}") # APIキーはログに出力しない

    try:
        response = requests.get(api_url, headers=headers)
        logger.info(f"ステータスコード: {response.status_code}")
        logger.info(f"レスポンス: {response.text}")

        # レスポンスの検証
        assert response.status_code == 200
        project = response.json()
        assert isinstance(project, dict)
        assert project["projectKey"] == project_key

        logger.info(f"テスト完了: test_get_project_by_key_direct")
    except Exception as e:
        logger.error(f"テスト失敗: {str(e)}")
        raise
