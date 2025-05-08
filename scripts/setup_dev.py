#!/usr/bin/env python3
"""
開発環境セットアップスクリプト
"""
import os
import subprocess
import sys
from pathlib import Path

def main():
    """開発環境をセットアップします"""
    print("BacklogMCP 開発環境セットアップをPoetryで開始します...")
    # プロジェクトルートディレクトリを取得
    root_dir = Path(__file__).parent.parent.absolute()
    os.chdir(root_dir)
    # Poetryによる依存解決と仮想環境構築
    print("Poetry依存関係をインストールしています...")
    subprocess.run([sys.executable, "-m", "poetry", "install"], check=True)
    print("セットアップが完了しました。`poetry shell`で開発環境に入ってください。")
    
    # .env.exampleが存在する場合は.envにコピー（既に存在する場合はスキップ）
    if (root_dir / ".env.example").exists() and not (root_dir / ".env").exists():
        print(".env.exampleを.envにコピーしています...")
        with open(root_dir / ".env.example", "r", encoding="utf-8") as f_src:
            with open(root_dir / ".env", "w", encoding="utf-8") as f_dst:
                f_dst.write(f_src.read())
        print(".envファイルを編集して、必要な環境変数を設定してください。")
    
    print("開発環境が整いました！")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
