#!/bin/bash
set -e

LAYER_DIR="build/lambda_layer"
PYTHON_PKG_DIR="${LAYER_DIR}/python"

# クリーンアップ
rm -rf ${LAYER_DIR}
mkdir -p ${PYTHON_PKG_DIR}

echo "Installing production dependencies to ${PYTHON_PKG_DIR}..."

# pyproject.toml と poetry.lock を一時的にコピーして、そのコンテキストでインストール
# これにより、プロジェクトルートの他のファイルに影響を与えずに依存関係のみを抽出できる
TEMP_POETRY_DIR=$(mktemp -d)
cp pyproject.toml poetry.lock ${TEMP_POETRY_DIR}/
# referenceディレクトリもコピー (pybacklogpyのため)
if [ -d "reference" ]; then
  cp -r reference ${TEMP_POETRY_DIR}/
fi

# Poetryで依存関係をエクスポートし、pipで指定ディレクトリにインストール
# Poetry 1.5+ では --only main でデフォルトグループを指定
# 古いバージョンでは --without dev などを使用
echo "Exporting dependencies from project root..."
/home/kusaka-server/.local/bin/poetry export --without-hashes --format=requirements.txt --only main > ${TEMP_POETRY_DIR}/requirements.txt
echo "Installing dependencies from exported requirements.txt..."
pip install --target ${PYTHON_PKG_DIR} -r ${TEMP_POETRY_DIR}/requirements.txt

# pybacklogpyが正しくインストールされているか確認 (オプション)
# poetry export がローカルの .whl ファイルパスを requirements.txt に正しく含め、
# pip install -r がそれを解決できることを期待しています。
# もし pybacklogpy がレイヤーに含まれない場合は、以下のコメントアウトを解除して
# 直接ホイールをインストールするなどの対策が必要になります。
#
# if [ -f "reference/pybacklogpy-0.12.1-py3-none-any.whl" ]; then
#   echo "Installing pybacklogpy from local wheel into layer..."
#   pip install --target ${PYTHON_PKG_DIR} reference/pybacklogpy-0.12.1-py3-none-any.whl
# fi

# 一時ディレクトリを削除
rm -rf ${TEMP_POETRY_DIR}

echo "Lambda layer content created in ${LAYER_DIR}"

# レイヤーに含めるべきではない大きなファイルや不要なファイルを削除 (例: .pyc, __pycache__)
find ${PYTHON_PKG_DIR} -type f -name '*.pyc' -delete
find ${PYTHON_PKG_DIR} -type d -name '__pycache__' -exec rm -rf {} +

echo "Lambda layer build complete."
