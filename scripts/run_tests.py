#!/usr/bin/env python3
"""
テスト実行スクリプト
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

def main():
    """テストを実行します"""
    parser = argparse.ArgumentParser(description="BacklogMCP テスト実行スクリプト")
    parser.add_argument("--unit", action="store_true", help="ユニットテストのみ実行")
    parser.add_argument("--integration", action="store_true", help="統合テストのみ実行")
    parser.add_argument("--e2e", action="store_true", help="E2Eテストのみ実行")
    parser.add_argument("--coverage", action="store_true", help="カバレッジレポートを生成")
    parser.add_argument("--verbose", "-v", action="store_true", help="詳細な出力")
    args = parser.parse_args()
    
    # プロジェクトルートディレクトリを取得
    root_dir = Path(__file__).parent.parent.absolute()
    os.chdir(root_dir)
    
    # テストコマンドの構築
    cmd = ["pytest"]
    
    # テストタイプの選択
    if args.unit:
        cmd.append("tests/unit/")
    elif args.integration:
        cmd.append("tests/integration/")
    elif args.e2e:
        cmd.append("tests/e2e/")
    
    # カバレッジオプション
    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=term", "--cov-report=html"])
    
    # 詳細出力オプション
    if args.verbose:
        cmd.append("-v")
    
    # テストの実行
    print(f"実行コマンド: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    # カバレッジレポートの場所を表示
    if args.coverage and result.returncode == 0:
        print("\nHTMLカバレッジレポートが生成されました:")
        print(f"file://{root_dir}/htmlcov/index.html")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
