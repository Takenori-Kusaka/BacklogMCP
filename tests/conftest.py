"""
pytest用の共通フィクスチャ
"""

import os
import signal
import socket
import subprocess
import time
from typing import Dict, Generator, List, Optional, Union
from unittest.mock import Mock

import pytest
from dotenv import load_dotenv

from tests.logger_config import setup_logger

# テスト用のロガー
logger = setup_logger("conftest", "conftest.log")

# .envファイルを読み込む
load_dotenv()

# モックモジュールをインポート
from tests.mocks import MockBacklogClient, MockIssueService, MockProjectService


@pytest.fixture
def mock_backlog_client() -> Mock:
    """
    モックのBacklogクライアント

    Returns:
        Mock: モックのBacklogクライアント
    """
    mock_client = Mock()

    # プロジェクト関連のメソッドのモック
    mock_client.get_projects.return_value = [
        {"id": 1, "projectKey": "TEST1", "name": "テストプロジェクト1"},
        {"id": 2, "projectKey": "TEST2", "name": "テストプロジェクト2"},
    ]

    mock_client.get_project.return_value = {
        "id": 1,
        "projectKey": "TEST1",
        "name": "テストプロジェクト1",
    }

    # チケット関連のメソッドのモック
    mock_client.get_issues.return_value = [
        {"id": 1, "issueKey": "TEST-1", "summary": "テスト課題1"},
        {"id": 2, "issueKey": "TEST-2", "summary": "テスト課題2"},
    ]

    mock_client.get_issue.return_value = {
        "id": 1,
        "issueKey": "TEST-1",
        "summary": "テスト課題1",
    }

    mock_client.create_issue.return_value = {
        "id": 1,
        "issueKey": "TEST-1",
        "summary": "新しい課題",
    }

    mock_client.update_issue.return_value = {
        "id": 1,
        "issueKey": "TEST-1",
        "summary": "更新された課題",
    }

    mock_client.delete_issue.return_value = True

    mock_client.add_comment.return_value = {"id": 1, "content": "テストコメント"}

    mock_client.get_issue_comments.return_value = [
        {"id": 1, "content": "コメント1"},
        {"id": 2, "content": "コメント2"},
    ]

    return mock_client


@pytest.fixture
def project_service(mock_backlog_client: Mock) -> MockProjectService:
    """
    プロジェクト管理サービス

    Args:
        mock_backlog_client: モックのBacklogクライアント

    Returns:
        MockProjectService: モックのプロジェクト管理サービス
    """
    return MockProjectService(backlog_client=mock_backlog_client)


@pytest.fixture
def issue_service(mock_backlog_client: Mock) -> MockIssueService:
    """
    課題管理サービス

    Args:
        mock_backlog_client: モックのBacklogクライアント

    Returns:
        MockIssueService: モックの課題管理サービス
    """
    return MockIssueService(backlog_client=mock_backlog_client)


def is_port_in_use(port: int) -> bool:
    """指定されたポートが使用中かどうかを確認する"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


@pytest.fixture(scope="session")
def mcp_server_process() -> Generator[str, None, None]:
    """
    テスト用のMCPサーバープロセスを起動するフィクスチャ
    
    Dockerコンテナ上で動作しているサーバーを使用します。
    環境変数 DOCKER_MCP_SERVER_URL でサーバーのURLを指定できます（デフォルト: http://localhost:8000）

    Returns:
        Generator[str, None, None]: MCPサーバーのURL
    """
    # Dockerで起動したサーバーのURLを使用
    server_url = os.getenv("DOCKER_MCP_SERVER_URL", "http://localhost:8000")
    logger.info(f"Docker環境のサーバーを使用します。URL: {server_url}")
    
    # サーバーが応答するか確認
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            import requests
            
            response = requests.get(f"{server_url}/")
            if response.status_code == 200:
                logger.info(f"Docker上のサーバーに接続成功: {response.status_code}")
                break
        except Exception as e:
            logger.info(f"Docker上のサーバーへの接続試行中... {str(e)}")
        
        time.sleep(1)
        retry_count += 1
    
    if retry_count >= max_retries:
        logger.error("Docker上のサーバーへの接続に失敗しました")
        raise Exception("Docker上のサーバーへの接続に失敗しました。Docker Composeでサーバーが起動しているか確認してください。")
    
    yield server_url
    
    # スクリプト側でコンテナを停止するため、ここでは何もしない
    logger.info("Docker環境のサーバーを使用しているため、ここでは停止処理を行いません")


@pytest.fixture(scope="session")
def mcp_server_url(mcp_server_process: str) -> str:
    """テスト実行時のMCPサーバーURLを返すfixture"""
    logger.info(f"MCPサーバーURL: {mcp_server_process}")
    return mcp_server_process


@pytest.fixture(scope="session")
def env_vars() -> Dict[str, Optional[str]]:
    """
    環境変数を読み込むフィクスチャ

    Returns:
        Dict[str, Optional[str]]: 環境変数の辞書
    """
    return {
        "api_key": os.getenv("BACKLOG_API_KEY"),
        "space": os.getenv("BACKLOG_SPACE"),
        "project": os.getenv("BACKLOG_PROJECT"),
    }


@pytest.fixture(scope="session")
def backlog_client(env_vars: Dict[str, Optional[str]]):
    """
    実際のBacklogクライアントのインスタンスを作成するフィクスチャ

    Args:
        env_vars: 環境変数の辞書

    Returns:
        Optional[BacklogClient]: 実際のBacklogクライアントのインスタンス
    """
    from app.infrastructure.backlog.backlog_client import BacklogClient

    # 環境変数が設定されていない場合はNoneを返す
    if not env_vars["api_key"] or not env_vars["space"]:
        return None

    return BacklogClient(api_key=env_vars["api_key"], space=env_vars["space"])
