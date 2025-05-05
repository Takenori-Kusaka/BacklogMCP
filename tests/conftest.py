"""
pytest用の共通フィクスチャ
"""
import os
import pytest
import subprocess
import time
import signal
import socket
from unittest.mock import Mock
from dotenv import load_dotenv
from tests.logger_config import setup_logger

# テスト用のロガー
logger = setup_logger('conftest', 'conftest.log')

# .envファイルを読み込む
load_dotenv()

# モックモジュールをインポート
from tests.mocks import MockBacklogClient, MockProjectService, MockIssueService


@pytest.fixture
def mock_backlog_client():
    """
    モックのBacklogクライアント
    
    Returns:
        Mock: モックのBacklogクライアント
    """
    mock_client = Mock()
    
    # プロジェクト関連のメソッドのモック
    mock_client.get_projects.return_value = [
        {"id": 1, "projectKey": "TEST1", "name": "テストプロジェクト1"},
        {"id": 2, "projectKey": "TEST2", "name": "テストプロジェクト2"}
    ]
    
    mock_client.get_project.return_value = {
        "id": 1, "projectKey": "TEST1", "name": "テストプロジェクト1"
    }
    
    # チケット関連のメソッドのモック
    mock_client.get_issues.return_value = [
        {"id": 1, "issueKey": "TEST-1", "summary": "テスト課題1"},
        {"id": 2, "issueKey": "TEST-2", "summary": "テスト課題2"}
    ]
    
    mock_client.get_issue.return_value = {
        "id": 1, "issueKey": "TEST-1", "summary": "テスト課題1"
    }
    
    mock_client.create_issue.return_value = {
        "id": 1, "issueKey": "TEST-1", "summary": "新しい課題"
    }
    
    mock_client.update_issue.return_value = {
        "id": 1, "issueKey": "TEST-1", "summary": "更新された課題"
    }
    
    mock_client.delete_issue.return_value = True
    
    mock_client.add_comment.return_value = {
        "id": 1, "content": "テストコメント"
    }
    
    mock_client.get_issue_comments.return_value = [
        {"id": 1, "content": "コメント1"},
        {"id": 2, "content": "コメント2"}
    ]
    
    return mock_client


@pytest.fixture
def project_service(mock_backlog_client):
    """
    プロジェクト管理サービス
    
    Args:
        mock_backlog_client: モックのBacklogクライアント
        
    Returns:
        MockProjectService: モックのプロジェクト管理サービス
    """
    return MockProjectService(backlog_client=mock_backlog_client)

@pytest.fixture
def issue_service(mock_backlog_client):
    """
    課題管理サービス
    
    Args:
        mock_backlog_client: モックのBacklogクライアント
        
    Returns:
        MockIssueService: モックの課題管理サービス
    """
    return MockIssueService(backlog_client=mock_backlog_client)

def is_port_in_use(port):
    """指定されたポートが使用中かどうかを確認する"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

@pytest.fixture(scope="session")
def mcp_server_process():
    """
    テスト用のMCPサーバープロセスを起動するフィクスチャ
    
    Returns:
        str: MCPサーバーのURL
    """
    # サーバーのポート
    port = 8000
    
    logger.info(f"サーバー起動準備: ポート {port} を使用")
    
    # ポートが既に使用されている場合は別のポートを使用
    while is_port_in_use(port):
        port += 1
        logger.info(f"ポート {port} を使用")
    
    # サーバーを起動
    logger.info(f"サーバー起動コマンド: python -m uvicorn app.main:app --host 127.0.0.1 --port {port}")
    
    # Windows環境での起動方法を改善
    if os.name == 'nt':
        # Windowsの場合は、shellをTrueにして、コマンドを文字列として渡す
        # pythonコマンドを使用して、uvicornを起動する
        server_process = subprocess.Popen(
            f"python -m uvicorn app.main:app --host 127.0.0.1 --port {port}",
            shell=True,
            # 標準出力と標準エラー出力を表示するためにPIPEを使用しない
            stdout=None,
            stderr=None
        )
    else:
        # Unix系の場合
        server_process = subprocess.Popen(
            ["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
            stdout=None,
            stderr=None,
            preexec_fn=os.setsid
        )
    
    logger.info(f"サーバープロセスID: {server_process.pid}")
    
    # サーバーの起動を待つ
    logger.info(f"サーバー起動待機開始: {time.time()}")
    
    # サーバーが実際に起動して応答するまで待機
    max_retries = 30
    retry_count = 0
    server_url = f"http://127.0.0.1:{port}"
    while retry_count < max_retries:
        try:
            import requests
            response = requests.get(f"{server_url}/")
            if response.status_code == 200:
                logger.info(f"サーバー起動確認: {response.status_code} {response.text[:100]}")
                break
        except Exception as e:
            logger.info(f"サーバー接続試行中... {str(e)}")
        
        time.sleep(1)
        retry_count += 1
        logger.info(f"サーバー起動待機中... {retry_count}/{max_retries}")

    if retry_count >= max_retries:
        logger.error(f"サーバー起動タイムアウト")
        raise Exception("サーバーの起動に失敗しました")

    logger.info(f"サーバー起動待機終了: {time.time()}")
    
    # サーバーのURLを返す
    logger.info(f"サーバーURL: {server_url}")
    
    yield server_url
    
    # テスト終了後にサーバーを停止
    logger.info(f"サーバー停止開始: {time.time()}")
    try:
        if os.name == 'nt':
            # Windowsの場合
            logger.info(f"Windows環境でサーバー停止: PID {server_process.pid}")
            # Windowsでは、プロセスツリーを終了するためにtaskkillを使用
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(server_process.pid)])
        else:
            # Unix系の場合
            logger.info(f"Unix環境でサーバー停止: PID {server_process.pid}")
            os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
        
        server_process.wait(timeout=5)  # 最大5秒待機
        logger.info(f"サーバー停止完了: {time.time()}")
    except Exception as e:
        logger.error(f"サーバー停止中にエラーが発生: {str(e)}")

# # 簡易的なmcp_server_processフィクスチャ
# @pytest.fixture(scope="session")
# def mcp_server_process():
#     """
#     テスト用のMCPサーバープロセスを起動するフィクスチャ（簡易版）
#     
#     Returns:
#         str: MCPサーバーのURL
#     """
#     # 手動で起動したサーバーのURLを返す
#     server_url = "http://127.0.0.1:8000"
#     logger.info(f"サーバーURL: {server_url}")
#     
#     yield server_url

@pytest.fixture(scope="session")
def mcp_server_url(mcp_server_process):
    """テスト実行時のMCPサーバーURLを返すfixture"""
    logger.info(f"MCPサーバーURL: {mcp_server_process}")
    return mcp_server_process

@pytest.fixture(scope="session")
def env_vars():
    """
    環境変数を読み込むフィクスチャ
    
    Returns:
        dict: 環境変数の辞書
    """
    return {
        "api_key": os.getenv("BACKLOG_API_KEY"),
        "space": os.getenv("BACKLOG_SPACE"),
        "project": os.getenv("BACKLOG_PROJECT")
    }

@pytest.fixture(scope="session")
def backlog_client(env_vars):
    """
    実際のBacklogクライアントのインスタンスを作成するフィクスチャ
    
    Args:
        env_vars: 環境変数の辞書
        
    Returns:
        BacklogClient: 実際のBacklogクライアントのインスタンス
    """
    from app.infrastructure.backlog.backlog_client import BacklogClient
    
    # 環境変数が設定されていない場合はNoneを返す
    if not env_vars["api_key"] or not env_vars["space"]:
        return None
    
    return BacklogClient(
        api_key=env_vars["api_key"],
        space=env_vars["space"]
    )
