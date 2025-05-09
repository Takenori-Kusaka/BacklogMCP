#!/bin/bash

# Node.jsのバージョンを確認
NODE_VERSION=$(node -v)
REQUIRED_VERSION="v14.15.0"

# バージョン比較関数
function version_lt() { 
    test "$(echo "$@" | tr " " "\n" | sort -rV | head -n 1)" != "$1"; 
}

# Node.jsのバージョンが必要なバージョンより低い場合は警告を表示
if version_lt "${NODE_VERSION}" "${REQUIRED_VERSION}"; then
    echo "警告: Node.jsのバージョンが古すぎます（${NODE_VERSION}）"
    echo "AWS CDKは Node.js ${REQUIRED_VERSION} 以上が必要です"
    echo "テストが失敗する可能性があります"
    echo ""
    echo "Node.jsをアップグレードするには以下のコマンドを実行してください："
    echo "  curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash - && sudo apt-get install -y nodejs"
    echo ""
    read -p "それでもテストを実行しますか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# テストを実行
echo "テストを実行中..."
npm test -- --no-cache --no-watchman
