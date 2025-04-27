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
    print("BacklogMCP 開発環境セットアップを開始します...")
    
    # プロジェクトルートディレクトリを取得
    root_dir = Path(__file__).parent.parent.absolute()
    os.chdir(root_dir)
    
    # 仮想環境の作成（既に存在する場合はスキップ）
    if not (root_dir / "venv").exists():
        print("仮想環境を作成しています...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    
    # 仮想環境のPythonとpipを取得
    if os.name == "nt":  # Windows
        python_exe = root_dir / "venv" / "Scripts" / "python.exe"
        pip_exe = root_dir / "venv" / "Scripts" / "pip.exe"
    else:  # Unix/Linux/Mac
        python_exe = root_dir / "venv" / "bin" / "python"
        pip_exe = root_dir / "venv" / "bin" / "pip"
    
    # 依存関係のインストール
    print("開発用依存関係をインストールしています...")
    subprocess.run([str(pip_exe), "install", "-r", "requirements/dev.txt"], check=True)
    
    # 開発モードでパッケージをインストール
    print("パッケージを開発モードでインストールしています...")
    subprocess.run([str(pip_exe), "install", "-e", "."], check=True)
    
    # .env.exampleが存在する場合は.envにコピー（既に存在する場合はスキップ）
    if (root_dir / ".env.example").exists() and not (root_dir / ".env").exists():
        print(".env.exampleを.envにコピーしています...")
        with open(root_dir / ".env.example", "r", encoding="utf-8") as f_src:
            with open(root_dir / ".env", "w", encoding="utf-8") as f_dst:
                f_dst.write(f_src.read())
        print(".envファイルを編集して、必要な環境変数を設定してください。")
    
    print("セットアップが完了しました！")
    print("開発を開始するには:")
    if os.name == "nt":  # Windows
        print(f"  {root_dir}\\venv\\Scripts\\activate")
    else:  # Unix/Linux/Mac
        print(f"  source {root_dir}/venv/bin/activate")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
