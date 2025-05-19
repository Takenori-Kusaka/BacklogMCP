"""
同期的なE2Eテスト実行のためのユーティリティ
"""

import json
import logging
import os
import time # time モジュールは直接使用されなくなる可能性があります
from typing import Any, Dict, List, Optional, Tuple, Union

import httpx # httpx は anyio と互換性があります
import anyio # anyio をインポート
from anyio.from_thread import start_blocking_portal # 同期コードから非同期を呼び出すために使用

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

from tests.logger_config import setup_logger

# テスト用のロガー
logger = setup_logger("sync_test_utils", "sync_test_utils.log")

# コンソール出力用のロガー
console_logger = logging.getLogger("console")
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
console_logger.addHandler(console_handler)
console_logger.setLevel(logging.INFO)


def log_step(message: str) -> None:
    """
    テストステップをログとコンソールに出力

    Args:
        message: ログメッセージ
    """
    logger.info(message)
    console_logger.info(message)

# call_mcp_tool_with_timeout は SyncMCPClient のメソッドに統合されます

def extract_json_from_mcp_result(result: Any) -> Any:
    """
    MCPの結果からJSONデータを抽出する

    Args:
        result: MCPの結果

    Returns:
        Any: 抽出したJSONデータ

    Raises:
        ValueError: JSONデータが見つからない場合
    """
    if not hasattr(result, "content") or not result.content:
        raise ValueError("MCPの結果にcontentがありません")
    
    for content_item in result.content:
        if hasattr(content_item, "text"):
            try:
                return json.loads(content_item.text)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSONのパースに失敗しました: {str(e)}")
    
    raise ValueError("MCPの結果にテキストコンテンツがありません")


class SyncMCPClient:
    """
    同期的なMCPクライアント
    
    非同期のMCPクライアントを同期的に使用するためのラッパークラス
    anyio.from_thread.start_blocking_portal を使用して実装
    """
    
    def __init__(self, server_url: str, timeout: int = 5):
        """
        初期化
        
        Args:
            server_url: MCPサーバーのURL
            timeout: デフォルトのタイムアウト（秒）
        """
        if not server_url.endswith("/mcp"):
            if server_url.endswith("/"):
                self.server_url = server_url + "mcp"
            else:
                self.server_url = server_url + "/mcp"
        else:
            self.server_url = server_url

        self.timeout = timeout
        self.session: Optional[ClientSession] = None
        self._sse_cm = None
        self._read = None
        self._write = None
        self._portal_cm = None  # start_blocking_portal()が返すコンテキストマネージャを保持
        self.portal: Optional[anyio.from_thread.BlockingPortal] = None # 実際のBlockingPortalインスタンスを保持

    async def _async_setup(self):
        """非同期セットアップ処理"""
        log_step(f"ダミーのSSEクライアントセットアップ開始 (接続先: {self.server_url})")
        # self._sse_cm = sse_client(self.server_url) # 本来のsse_client呼び出しをコメントアウト
        self._sse_cm = True # _async_cleanup が実行されるようにダミーで設定
        read, write = "dummy_read_stream", "dummy_write_stream" # ダミーの値を設定
        try:
            log_step(f"ダミーのSSE __aenter__ 相当の処理開始 (anyio.sleep)")
            # portal.call が提供する CancelScope 内で実行される
            await anyio.sleep(0.01) # sse_client.__aenter__ の代わりに simple sleep
            
            log_step(f"ダミーのSSE __aenter__ 相当の処理完了")

            # ダミー処理なので、read/write のチェックは不要
            # if read is None or write is None:
            #     log_step(f"SSEクライアント作成失敗 (read/write is None) - 接続先: {self.server_url}")
            #     raise RuntimeError("SSE client setup failed to return read/write streams.")

        except Exception as e:
            log_step(f"ダミーのSSEセットアップ中に予期せぬエラー: {type(e).__name__} - {str(e)}")
            raise
        
        log_step("ダミーのSSEセットアップ完了")
        self._read = read
        self._write = write
        
        # ClientSessionの初期化はコメントアウトしたまま。
        # これにより、call_tool で self.session が None であるためエラーが発生し、
        # CancelScopeの問題とは異なる箇所でテストが失敗することを示す。
        # log_step("ClientSession作成開始")
        # self.session = ClientSession(self._read, self._write)
        # await self.session.__aenter__()
        # log_step("ClientSession作成完了")
        #
        # log_step("MCPクライアント初期化開始")
        # await self.session.initialize()
        # log_step("MCPクライアント初期化完了")
        log_step("ダミーのSSEクライアントのみのセットアップ完了 (セッション未初期化)")


    async def _async_cleanup(self, exc_type, exc_val, exc_tb):
        """非同期クリーンアップ処理"""
        log_step("非同期クリーンアップ開始")
        # ClientSessionのクリーンアップもコメントアウト
        # if self.session:
        #     log_step("ClientSession終了処理開始")
        #     try:
        #         await self.session.__aexit__(exc_type, exc_val, exc_tb)
        #     except Exception as e:
        #         log_step(f"ClientSession終了処理中にエラー: {type(e).__name__} - {str(e)}")
        #     finally:
        #         log_step("ClientSession終了処理完了")
        
        if self._sse_cm: # self._sse_cm はダミーでTrueになっている
            log_step(f"ダミーのSSEクライアント終了処理開始")
            try:
                # portal.call が提供する CancelScope 内で実行される
                await anyio.sleep(0.01) # sse_client.__aexit__ の代わりに simple sleep
                
                log_step("ダミーのSSEクライアント終了処理完了")

            except Exception as e:
                log_step(f"ダミーのSSEクライアント終了処理中にエラー: {type(e).__name__} - {str(e)}")
            finally:
                log_step("ダミーのSSEクライアント終了処理の試行完了")
        log_step("非同期クリーンアップ完了")

    def __enter__(self):
        log_step(f"MCPクライアント接続開始: {self.server_url}")
        self._portal_cm = start_blocking_portal()
        self.portal = self._portal_cm.__enter__() # コンテキストマネージャからBlockingPortalインスタンスを取得
        
        if not self.portal or not hasattr(self.portal, 'call'):
            log_step(f"致命的エラー: ポータルオブジェクトの取得に失敗しました。型: {type(self.portal)}")
            raise RuntimeError(f"Failed to obtain a valid portal object. Portal type: {type(self.portal)}")

        log_step("setup 呼び出し開始")
        self.portal.call(self._async_setup)
        log_step("setup 呼び出し完了")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        log_step("MCPクライアント接続終了")
        
        if self.portal: # BlockingPortalインスタンス経由で非同期クリーンアップを実行
            log_step("非同期クリーンアップ処理開始 (portal.call)")
            try:
                self.portal.call(self._async_cleanup, exc_type, exc_val, exc_tb)
            except Exception as e:
                log_step(f"portal.call(_async_cleanup) 実行中にエラー: {type(e).__name__} - {str(e)}")
        
        if self._portal_cm: # コンテキストマネージャ自体の終了処理
            log_step("ポータルコンテキストマネージャ終了処理開始 (_portal_cm.__exit__)")
            try:
                self._portal_cm.__exit__(exc_type, exc_val, exc_tb)
                log_step("ポータルコンテキストマネージャ終了処理完了")
            except Exception as e:
                log_step(f"_portal_cm.__exit__ 実行中にエラー: {type(e).__name__} - {str(e)}")
        elif self.portal and not self._portal_cm and hasattr(self.portal, 'close'):
            # このケースは通常発生しないはずだが、念のため
            log_step("警告: _portal_cm が設定されていませんが、portal は存在し close 可能です。portal.close() を試みます。")
            try:
                self.portal.close()
            except Exception as e:
                 log_step(f"portal.close() 実行中にエラー: {type(e).__name__} - {str(e)}")
        else:
            log_step("ポータルまたはポータルコンテキストマネージャが見つからないため、終了処理の一部または全部をスキップします。")


    async def _async_call_tool(self, tool_name: str, arguments: Dict[str, Any], timeout_duration: int) -> Any:
        """MCPツールを非同期で呼び出す内部メソッド"""
        if not self.session:
            # この状態は通常 __enter__ でセッションが確立されるため発生しないはず
            raise RuntimeError("セッションが初期化されていません (非同期呼び出し内部)")

        log_step(f"ツール呼び出し開始 (非同期): {tool_name} - 引数: {json.dumps(arguments, ensure_ascii=False)}")
        result = None
        try:
            with anyio.move_on_after(timeout_duration) as scope:
                result = await self.session.call_tool(tool_name, arguments)

            if scope.cancel_called:
                log_step(f"ツール呼び出しタイムアウト: {tool_name} - {timeout_duration}秒経過")
                raise TimeoutError(f"ツール呼び出しがタイムアウトしました: {tool_name}")

            # レスポンス内容をログに出力
            try:
                result_content = json.dumps(result.model_dump(), ensure_ascii=False, indent=2)
                log_step(f"ツール呼び出し成功: {tool_name} - 結果: {result_content}")
            except Exception as e:
                log_step(f"ツール呼び出し成功: {tool_name} - 結果のJSON変換に失敗: {str(e)}")
                log_step(f"ツール呼び出し成功: {tool_name} - 結果 (raw): {result}")
            
            return result
        except Exception as e: # TimeoutError もここでキャッチされる
            if not isinstance(e, TimeoutError): # TimeoutErrorでなければログ出力と型変換
                log_step(f"ツール呼び出しエラー: {tool_name} - repr(e): {repr(e)} - str(e): {str(e)}")
                # ここで予期せぬエラーをTimeoutErrorにラップすべきか、そのまま伝播させるか検討
                # 現状はそのまま伝播
            raise


    def call_tool(self, tool_name: str, arguments: Dict[str, Any], timeout: Optional[int] = None) -> Any:
        if not self.portal:
            raise RuntimeError("ポータルが初期化されていません。__enter__が呼び出されましたか？")

        actual_timeout = timeout if timeout is not None else self.timeout
        
        return self.portal.call(self._async_call_tool, tool_name, arguments, actual_timeout)

    def get_json_result(self, tool_name: str, arguments: Dict[str, Any], timeout: Optional[int] = None) -> Any:
        """
        ツールを呼び出してJSON結果を取得
        
        Args:
            tool_name: ツール名
            arguments: 引数
            timeout: タイムアウト（秒）
        
        Returns:
            Any: 抽出したJSONデータ
        """
        result = self.call_tool(tool_name, arguments, timeout)
        return extract_json_from_mcp_result(result)
