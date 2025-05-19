# ビルドステージ - 依存関係のインストールのみを行う
FROM python:3.12-slim AS builder

WORKDIR /build

# 必要なパッケージをインストール
COPY dependencies/pybacklogpy-0.12.1-py3-none-any.whl ./dependencies/pybacklogpy-0.12.1-py3-none-any.whl

# 必要な依存関係のみをインストール
RUN pip install --no-cache-dir --target=/build/deps \
    fastapi==0.115.12 \
    uvicorn[standard]==0.34.2 \
    pydantic==2.11.3 \
    httpx==0.28.1 \
    python-dotenv==1.1.0 \
    fastapi-mcp==0.3.3 \
    mangum==0.19.0 \
    requests \
    ./dependencies/pybacklogpy-0.12.1-py3-none-any.whl

# uvicornをグローバルにインストール（コマンドラインから実行できるように）
RUN pip install --no-cache-dir uvicorn[standard]==0.34.2

# 実行環境ステージ - 必要最小限のイメージを作成
FROM python:3.12-slim AS runtime

WORKDIR /app

# ヘルスチェック用のcurlのみをインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ビルドステージから依存関係をコピー
COPY --from=builder /build/deps /usr/local/lib/python3.12/site-packages/

# アプリケーションコードのみをコピー
COPY app/ ./app/

# 環境変数の設定
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# ポートの公開
EXPOSE 8000

# Mangumを使用したLambdaハンドラー
CMD ["python", "-c", "from app.main import handler; import sys; handler(sys.stdin.read(), None)"]
