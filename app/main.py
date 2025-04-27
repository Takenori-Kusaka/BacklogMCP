"""
BacklogMCP - メインアプリケーション
"""
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP
from dotenv import load_dotenv
from mangum import Mangum

# 環境変数の読み込み
load_dotenv()

# APIルーターのインポート
from app.presentation.api.project_router import router as project_router

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

# APIルーターの登録
app.include_router(project_router)

# MCPサーバーの作成
mcp_server = FastApiMCP(
    fastapi=app,
    name="BacklogMCP",
    description="Backlog SaaSをModel Context Protocol (MCP)経由で操作するためのAPI",
)

# MCPサーバーをマウント
mcp_server.mount(mount_path="/mcp")

# グローバル例外ハンドラー
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    グローバル例外ハンドラー
    
    Args:
        request: リクエスト
        exc: 例外
        
    Returns:
        JSONResponse: エラーレスポンス
    """
    return JSONResponse(
        status_code=500,
        content={"error": f"Internal Server Error: {str(exc)}"}
    )

# ルートエンドポイント
@app.get("/")
async def root():
    """
    ルートエンドポイント
    
    Returns:
        dict: ウェルカムメッセージ
    """
    return {
        "message": "Welcome to BacklogMCP API",
        "docs": "/docs",
        "mcp": "/mcp"
    }

# AWS Lambda用ハンドラー
handler = Mangum(app)

# 開発サーバー起動用関数
def start():
    """
    開発サーバーを起動
    """
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True
    )

# スクリプトとして実行された場合
if __name__ == "__main__":
    start()
