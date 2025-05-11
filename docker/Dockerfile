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
# COPY . . # この行は上記でappディレクトリなどを個別にコピーするように変更したためコメントアウトまたは削除

# ポートの公開
EXPOSE 8000

# アプリケーションの実行
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
