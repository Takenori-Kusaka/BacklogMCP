FROM python:3.12-slim

WORKDIR /app

# 依存関係のインストール
COPY pyproject.toml ./
# poetry.lockファイルがある場合はコピー
COPY poetry.lock* ./

# poetryをインストールし、依存関係をインストール
# pybacklogpyパッケージはPyPIから直接インストール
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    # --no-rootオプションを使用して、プロジェクト自体をインストールしない
    poetry install --no-root || true && \
    pip install pybacklogpy==0.12

# アプリケーションのコピー
COPY app/ ./app/

# 環境変数の設定
ENV PYTHONPATH=/app

# ポートの公開
EXPOSE 8000

# Mangumを使用したLambdaハンドラー
CMD ["python", "-c", "from app.main import handler; import sys; handler(sys.stdin.read(), None)"]
