"""
BacklogMCP - メインアプリケーション
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.status import HTTP_403_FORBIDDEN
from fastapi_mcp import FastApiMCP  # type: ignore

from app.core.config import settings
from mangum import Mangum

# 環境変数の読み込み
load_dotenv()

from app.presentation.api.bulk_operations_router import router as bulk_operations_router
from app.presentation.api.issue_router import router as issue_router
from app.presentation.api.priority_router import router as priority_router

# APIルーターのインポート
from app.presentation.api.project_router import router as project_router
from app.presentation.api.user_router import router as user_router

# FastAPIアプリケーションの作成
app = FastAPI(
    title="BacklogMCP",
    description="Backlog SaaSをModel Context Protocol (MCP)経由で操作するためのAPI",
    version="0.1.0",
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限すること
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Read-only mode middleware
@app.middleware("http")
async def read_only_middleware(request: Request, call_next):
    if settings.READ_ONLY_MODE and request.method in ("POST", "PUT", "DELETE", "PATCH"):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Application is in read-only mode. Write operations are disabled.",
        )
    response = await call_next(request)
    return response

# APIルーターの登録
app.include_router(project_router)
app.include_router(issue_router)
app.include_router(bulk_operations_router)
app.include_router(user_router)
app.include_router(priority_router)

# MCPサーバーの作成
print("[DEBUG] MCPサーバー作成開始")
mcp_server = FastApiMCP(
    fastapi=app,
    name="BacklogMCP",
    description="Backlog SaaSをModel Context Protocol (MCP)経由で操作するためのAPI",
)
print("[DEBUG] MCPサーバー作成完了")

# MCPサーバーの設定
# FastApiMCP 0.3.3では、FastAPIのエンドポイントを自動的にMCPツールとして登録するため、
# カスタムツールのインポートは不要です。
print("[DEBUG] MCPサーバー設定開始")

# MCPサーバーの設定を更新
mcp_server.setup_server()
print("[DEBUG] MCPサーバー設定完了")

# 登録されたツールの一覧を表示
print("[DEBUG] 登録されたMCPツール一覧:")
try:
    # FastApiMCP 0.3.3では、toolsプロパティを使用してツール一覧を取得
    if hasattr(mcp_server, "tools"):
        for tool in mcp_server.tools:
            print(f"[DEBUG] - ツール名: {tool.name}")
    else:
        print("[DEBUG] - ツール一覧を取得できません")
except Exception as e:
    print(f"[DEBUG] - ツール一覧取得エラー: {str(e)}")

# MCPサーバーをマウント
print("[DEBUG] MCPサーバーマウント開始")
mcp_server.mount(mount_path="/mcp")
print("[DEBUG] MCPサーバーマウント完了")


# グローバル例外ハンドラー
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    グローバル例外ハンドラー

    Args:
        request: リクエスト
        exc: 例外

    Returns:
        JSONResponse: エラーレスポンス
    """
    return JSONResponse(
        status_code=500, content={"error": f"Internal Server Error: {str(exc)}"}
    )


# ルートエンドポイント
@app.get("/")
async def root() -> dict:
    """
    ルートエンドポイント

    Returns:
        dict: ウェルカムメッセージ
    """
    return {"message": "Welcome to BacklogMCP API", "docs": "/docs", "mcp": "/mcp"}


# AWS Lambda用ハンドラー
handler = Mangum(app)


# 開発サーバー起動用関数
def start() -> None:
    """
    開発サーバーを起動
    """
    import uvicorn

    # 開発環境では0.0.0.0を使用し、本番環境では特定のインターフェースを使用する
    # セキュリティ上の理由から、デフォルトではlocalhostを使用
    host = os.getenv("HOST", "127.0.0.1")
    uvicorn.run(
        "app.main:app", host=host, port=int(os.getenv("PORT", "8000")), reload=True
    )


# スクリプトとして実行された場合
if __name__ == "__main__":
    start()
