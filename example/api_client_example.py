"""
Backlog MCP API クライアント使用例

このスクリプトは、BacklogMCPプロジェクトのホスティングされたAPIに
HTTPリクエストを送信して、Backlogの課題を操作する方法を示します。
"""
import os
import sys
import json
import requests
from datetime import datetime

# APIのベースURL（デフォルトはローカルのDocker環境）
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
# APIのエンドポイントプレフィックス
API_PREFIX = "/api"

def print_json(data):
    """JSONデータを整形して表示"""
    print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    # 環境変数からBacklog APIの設定を取得
    api_key = os.getenv("BACKLOG_API_KEY")
    space = os.getenv("BACKLOG_SPACE")
    project_key = os.getenv("BACKLOG_PROJECT")
    
    if not api_key or not space:
        print("環境変数 BACKLOG_API_KEY と BACKLOG_SPACE を設定してください。")
        return
    
    if not project_key:
        print("環境変数 BACKLOG_PROJECT が設定されていません。プロジェクト一覧から選択してください。")
    
    # 1. プロジェクト一覧の取得
    print("\n=== プロジェクト一覧 ===")
    try:
        response = requests.get(f"{API_BASE_URL}{API_PREFIX}/projects")
        response.raise_for_status()
        projects = response.json()
        
        for project in projects:
            print(f"- {project['name']} (キー: {project['projectKey']}, ID: {project['id']})")
        
        # プロジェクトキーが設定されていない場合は最初のプロジェクトを使用
        if not project_key and projects:
            project_key = projects[0]["projectKey"]
            print(f"\nプロジェクト '{project_key}' を使用します。")
        
        if not project_key:
            print("利用可能なプロジェクトがありません。")
            return
    except requests.exceptions.RequestException as e:
        print(f"プロジェクト一覧の取得に失敗しました: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"エラーレスポンス: {e.response.text}")
        return
    
    # 2. プロジェクト詳細の取得
    print(f"\n=== プロジェクト '{project_key}' の詳細 ===")
    try:
        response = requests.get(f"{API_BASE_URL}{API_PREFIX}/projects/{project_key}")
        response.raise_for_status()
        project = response.json()
        
        print(f"名前: {project['name']}")
        print(f"キー: {project['projectKey']}")
        print(f"ID: {project['id']}")
    except requests.exceptions.RequestException as e:
        print(f"プロジェクト詳細の取得に失敗しました: {e}")
        return
    
    # 3. ユーザー一覧の取得
    print("\n=== ユーザー一覧 ===")
    try:
        response = requests.get(f"{API_BASE_URL}{API_PREFIX}/users")
        response.raise_for_status()
        users = response.json()
        
        for user in users:
            print(f"- {user['name']} (ID: {user['id']})")
    except requests.exceptions.RequestException as e:
        print(f"ユーザー一覧の取得に失敗しました: {e}")
        users = []
    
    # 4. 優先度一覧の取得
    print("\n=== 優先度一覧 ===")
    try:
        response = requests.get(f"{API_BASE_URL}{API_PREFIX}/priorities")
        response.raise_for_status()
        priorities = response.json()
        
        for priority in priorities:
            print(f"- {priority['name']} (ID: {priority['id']})")
    except requests.exceptions.RequestException as e:
        print(f"優先度一覧の取得に失敗しました: {e}")
        priorities = []
    
    # 5. ステータス一覧の取得
    print(f"\n=== プロジェクト '{project_key}' のステータス一覧 ===")
    try:
        response = requests.get(f"{API_BASE_URL}{API_PREFIX}/projects/{project_key}/statuses")
        response.raise_for_status()
        statuses = response.json()
        
        for status in statuses:
            print(f"- {status['name']} (ID: {status['id']})")
    except requests.exceptions.RequestException as e:
        print(f"ステータス一覧の取得に失敗しました: {e}")
        statuses = []
    
    # 6. 課題一覧の取得
    print(f"\n=== プロジェクト '{project_key}' の課題一覧 ===")
    try:
        response = requests.get(
            f"{API_BASE_URL}{API_PREFIX}/issues",
            params={"project_id": project["id"], "count": 5}
        )
        response.raise_for_status()
        issues = response.json()
        
        for issue in issues:
            print(f"- {issue['summary']} (キー: {issue['issueKey']}, ID: {issue['id']})")
    except requests.exceptions.RequestException as e:
        print(f"課題一覧の取得に失敗しました: {e}")
        issues = []
    
    # 7. 課題の種別一覧を取得
    try:
        # 注意: このエンドポイントはサンプルアプリケーションに実装されていない場合があります
        # その場合は、BacklogClientを直接使用するか、Backlog APIを直接呼び出す必要があります
        response = requests.get(f"{API_BASE_URL}{API_PREFIX}/projects/{project_key}/issue-types")
        response.raise_for_status()
        issue_types = response.json()
    except requests.exceptions.RequestException as e:
        print(f"課題の種別一覧の取得に失敗しました: {e}")
        print("サンプルの課題種別を使用します。")
        # サンプルの課題種別を使用
        issue_types = [{"id": 1, "name": "タスク"}]
    
    # 8. 課題の作成（名前ベースのパラメータを使用）
    print("\n=== 課題の作成 ===")
    
    # 必要なデータが取得できているか確認
    if not issue_types:
        print("課題の種別が取得できないため、課題を作成できません。")
        return
    
    # 最初の課題種別を使用
    issue_type_name = issue_types[0]["name"]
    
    # 優先度が取得できていれば最初の優先度を使用
    priority_name = priorities[0]["name"] if priorities else None
    
    # ユーザーが取得できていれば最初のユーザーを担当者に設定
    assignee_name = users[0]["name"] if users else None
    
    # 現在時刻をタイムスタンプとして使用
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 課題作成リクエスト
    try:
        issue_data = {
            "project_key": project_key,
            "summary": f"APIサンプル課題 {timestamp}",
            "description": "これはBacklog MCP APIを使用して作成されたサンプル課題です。",
            "issue_type_name": issue_type_name
        }
        
        # オプションのパラメータを追加
        if priority_name:
            issue_data["priority_name"] = priority_name
        if assignee_name:
            issue_data["assignee_name"] = assignee_name
        
        response = requests.post(
            f"{API_BASE_URL}{API_PREFIX}/issues",
            json=issue_data
        )
        response.raise_for_status()
        new_issue = response.json()
        
        print(f"課題が作成されました: {new_issue['summary']} (キー: {new_issue['issueKey']})")
    except requests.exceptions.RequestException as e:
        print(f"課題の作成に失敗しました: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"エラーレスポンス: {e.response.text}")
        return
    
    # 9. 課題の更新（名前ベースのパラメータを使用）
    print("\n=== 課題の更新 ===")
    
    # ステータスが取得できていれば2番目のステータス（通常は「処理中」）を使用
    status_name = statuses[1]["name"] if len(statuses) > 1 else None
    
    if not status_name:
        print("ステータスが取得できないため、課題を更新できません。")
        return
    
    # 課題更新リクエスト
    try:
        update_data = {
            "summary": f"更新されたAPIサンプル課題 {timestamp}",
            "status_name": status_name
        }
        
        response = requests.patch(
            f"{API_BASE_URL}{API_PREFIX}/issues/{new_issue['issueKey']}",
            json=update_data
        )
        response.raise_for_status()
        updated_issue = response.json()
        
        print(f"課題が更新されました: {updated_issue['summary']} (キー: {updated_issue['issueKey']})")
        print(f"新しいステータス: {updated_issue['status']['name']}")
    except requests.exceptions.RequestException as e:
        print(f"課題の更新に失敗しました: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"エラーレスポンス: {e.response.text}")
        return
    
    # 10. コメントの追加
    print("\n=== コメントの追加 ===")
    try:
        comment_data = {
            "content": f"これはAPIを使用して追加されたサンプルコメントです。({timestamp})"
        }
        
        response = requests.post(
            f"{API_BASE_URL}{API_PREFIX}/issues/{new_issue['issueKey']}/comments",
            json=comment_data
        )
        response.raise_for_status()
        comment = response.json()
        
        print(f"コメントが追加されました: ID {comment.get('id')}")
    except requests.exceptions.RequestException as e:
        print(f"コメントの追加に失敗しました: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"エラーレスポンス: {e.response.text}")
    
    # 11. コメント一覧の取得
    print("\n=== コメント一覧の取得 ===")
    try:
        response = requests.get(
            f"{API_BASE_URL}{API_PREFIX}/issues/{new_issue['issueKey']}/comments"
        )
        response.raise_for_status()
        comments = response.json()
        
        print(f"コメント数: {len(comments)}")
        for comment in comments:
            content = comment.get('content', '')
            if content:
                print(f"- ID: {comment.get('id')}, 内容: {content[:50]}...")
            else:
                print(f"- ID: {comment.get('id')}, 内容: なし")
    except requests.exceptions.RequestException as e:
        print(f"コメント一覧の取得に失敗しました: {e}")

if __name__ == "__main__":
    main()
