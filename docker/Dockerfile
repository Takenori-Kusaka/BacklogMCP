FROM python:3.12-slim

WORKDIR /app

# 依存関係のインストール
COPY pyproject.toml ./
# poetry.lockファイルがある場合はコピー
COPY poetry.lock* ./
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    # --no-rootオプションを使用して、プロジェクト自体をインストールしない
    poetry install --no-root

# アプリケーションのコピー
COPY . .

# pybacklogpyのインストール
RUN pip install reference/pybacklogpy-0.12.1-py3-none-any.whl

# ポートの公開
EXPOSE 8000

# アプリケーションの実行
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
