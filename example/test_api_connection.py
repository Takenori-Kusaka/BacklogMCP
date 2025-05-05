"""
API接続テスト

このスクリプトは、Backlog APIへの接続をテストします。
"""
import os
import sys
import requests
import json

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_direct_api():
    """
    直接Backlog APIに接続してテスト
    """
    api_key = os.getenv("BACKLOG_API_KEY", "test_api_key")
    space = os.getenv("BACKLOG_SPACE", "test_space")
    
    print(f"=== 直接Backlog APIに接続 ===")
    print(f"Space: {space}")
    print(f"API Key: {api_key[:4]}...{api_key[-4:] if len(api_key) > 8 else ''}")
    
    try:
        # SSL検証を無効化（テスト環境でのみ使用）
        url = f"https://{space}.backlog.com/api/v2/projects?apiKey={api_key}"
        response = requests.get(url, verify=False)
        print(f"ステータスコード: {response.status_code}")
        print(f"レスポンス: {response.text[:200]}...")
    except Exception as e:
        print(f"エラー: {e}")

def test_local_api():
    """
    ローカルAPIに接続してテスト
    """
    print(f"\n=== ローカルAPIに接続 ===")
    
    try:
        # ルートエンドポイントにアクセス
        url = "http://localhost:8000/"
        response = requests.get(url)
        print(f"ルートエンドポイント - ステータスコード: {response.status_code}")
        print(f"レスポンス: {response.text}")
        
        # プロジェクト一覧エンドポイントにアクセス
        url = "http://localhost:8000/api/projects"
        response = requests.get(url)
        print(f"\nプロジェクト一覧 - ステータスコード: {response.status_code}")
        if response.status_code == 200:
            print(f"レスポンス: {response.text[:200]}...")
        else:
            print(f"エラーレスポンス: {response.text}")
        
        # MCPエンドポイントにアクセス
        url = "http://localhost:8000/mcp"
        response = requests.get(url)
        print(f"\nMCPエンドポイント - ステータスコード: {response.status_code}")
        print(f"レスポンス: {response.text[:200]}...")
    except Exception as e:
        print(f"エラー: {e}")

def test_env_vars():
    """
    環境変数をテスト
    """
    print(f"\n=== 環境変数 ===")
    print(f"BACKLOG_API_KEY: {'設定済み' if os.getenv('BACKLOG_API_KEY') else '未設定'}")
    print(f"BACKLOG_SPACE: {'設定済み' if os.getenv('BACKLOG_SPACE') else '未設定'}")
    print(f"BACKLOG_PROJECT: {'設定済み' if os.getenv('BACKLOG_PROJECT') else '未設定'}")

if __name__ == "__main__":
    test_env_vars()
    test_local_api()
    test_direct_api()
