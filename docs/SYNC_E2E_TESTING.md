# 同期的なE2Eテスト実行ガイド

このドキュメントでは、BacklogMCPの同期的なE2Eテスト実行方法について説明します。従来の非同期テストでは実行状況が見えにくく、応答が得られない問題がありましたが、同期テストではこれらの問題を解決しています。

## 改善点

従来のE2Eテストと比較して、以下の点が改善されています：

1. **同期的な実行**: 非同期テストを同期的に実行することで、テストの実行状況が明確になりました
2. **詳細なログ出力**: 各テストステップでコンソールにも明確なログを出力するようになりました
3. **タイムアウト設定の最適化**: サーバー起動待ちやAPIリクエストのタイムアウトを5秒程度に短縮しました
4. **Docker環境のシンプル化**: テスト専用のDocker Compose設定を作成し、ヘルスチェック機能を強化しました
5. **エラー時の詳細情報表示**: エラーが発生した場合に詳細な情報を表示するようになりました
6. **テストカバレッジの拡大**: 課題、プロジェクト、バルク操作に関する多様なテストケースを追加しました

## 前提条件

以下のソフトウェアがインストールされていることを確認してください：

1. Docker
2. Docker Compose
3. Poetry（Pythonパッケージ管理）
4. Bash（シェルスクリプト実行用）

## 同期的なE2Eテスト実行手順

### 1. 環境変数の設定

以下の環境変数を設定します。これらはDockerコンテナ内のBacklogMCPサーバーで使用されます：

```bash
export BACKLOG_API_KEY=あなたのBacklog APIキー
export BACKLOG_SPACE=あなたのBacklogスペース名
export BACKLOG_PROJECT=テスト対象のプロジェクトキー
export BACKLOG_DISABLE_SSL_VERIFY=false  # 必要に応じてtrueに設定
```

### 2. 同期的なE2Eテストの実行

プロジェクトのルートディレクトリで以下のコマンドを実行します：

```bash
# すべての同期テストを実行
bash scripts/run_sync_e2e_test.sh

# 特定のテストファイルを実行
bash scripts/run_sync_e2e_test.sh tests/e2e/test_issue_sync_e2e.py

# 特定のテスト関数を実行
bash scripts/run_sync_e2e_test.sh tests/e2e/test_issue_sync_e2e.py::test_get_issues_from_real_api
```

また、特定のテストを簡単に実行するための専用スクリプトも用意されています：

```bash
# 特定のテストファイルまたはテスト関数を実行
bash scripts/run_specific_sync_test.sh test_issue_sync_e2e.py
bash scripts/run_specific_sync_test.sh test_project_sync_e2e.py::test_get_project_by_key
bash scripts/run_specific_sync_test.sh test_bulk_operations_sync_e2e.py::test_bulk_update_status_e2e
```

これらのスクリプトは以下の処理を行います：

1. Docker Composeを使用してBacklogMCPサーバーをビルドして起動
2. サーバーが正常に起動するのを待機（最大10秒）
3. 指定された同期テストを実行
4. テスト完了後にDockerコンテナを停止

## 利用可能な同期テスト

現在、以下の同期テストが実装されています：

### 課題関連のテスト (`tests/e2e/test_issue_sync_e2e.py`)

- `test_get_issues_from_real_api`: 課題一覧を取得するテスト
- `test_get_issue_by_key`: 特定の課題を取得するテスト
- `test_create_issue_with_name_parameters`: 名前ベースのパラメータで課題を作成するテスト

### プロジェクト関連のテスト (`tests/e2e/test_project_sync_e2e.py`)

- `test_get_projects_from_real_api`: プロジェクト一覧を取得するテスト
- `test_get_project_by_key`: 特定のプロジェクトを取得するテスト
- `test_get_project_users`: プロジェクトのユーザー一覧を取得するテスト
- `test_get_project_with_invalid_key`: 存在しないプロジェクトキーでプロジェクトを取得しようとするテスト

### バルク操作関連のテスト (`tests/e2e/test_bulk_operations_sync_e2e.py`)

- `test_bulk_update_status_e2e`: 複数チケットのステータスを一括更新するテスト
- `test_bulk_delete_issues_e2e`: 複数チケットを一括削除するテスト
- `test_bulk_update_status_with_invalid_request`: 不正なリクエストボディのバリデーションテスト
- `test_bulk_update_assignee_e2e`: 複数チケットの担当者を一括更新するテスト
- `test_bulk_update_category_e2e`: 複数チケットのカテゴリを一括更新するテスト

## 同期テストの実装方法

既存の非同期テストを同期テストに変換する方法は以下の通りです：

1. `tests/e2e/sync_test_utils.py`の`SyncMCPClient`クラスを使用する
2. `@pytest.mark.asyncio`デコレータを削除し、通常の同期関数として実装する
3. 各テストステップで`log_step`関数を使用してログを出力する
4. テストの開始と終了を明示的にログに記録する

例：

```python
def test_get_issues_from_real_api(mcp_server_url: str) -> None:
    """FastAPIサーバー経由で課題一覧を取得する同期的なE2Eテスト"""
    # テスト開始をログに記録
    log_step("テスト開始: test_get_issues_from_real_api")
    
    # 環境変数のチェック
    if not os.getenv("BACKLOG_API_KEY") or not os.getenv("BACKLOG_SPACE") or not os.getenv("BACKLOG_PROJECT"):
        pytest.skip("Backlog API環境変数が設定されていません")
    
    # 同期的なMCPクライアントを使用
    with SyncMCPClient(mcp_server_url, timeout=5) as client:
        # 課題一覧取得
        log_step("課題一覧取得を実行")
        try:
            issues = client.get_json_result("get_issues", {})
            
            # 結果の検証
            assert isinstance(issues, list)
            log_step(f"取得した課題数: {len(issues)}")
            
            # 課題が存在する場合のみ検証
            if issues:
                assert "id" in issues[0]
                assert "issueKey" in issues[0]
                assert "summary" in issues[0]
                log_step(f"最初の課題: {issues[0]['issueKey']} - {issues[0]['summary']}")
            else:
                log_step("課題が見つかりませんでした")
        except Exception as e:
            log_step(f"エラーが発生しました: {str(e)}")
            raise
    
    # テスト終了をログに記録
    log_step("テスト終了: test_get_issues_from_real_api")
```

## トラブルシューティング

### サーバー起動の問題

サーバーの起動に問題がある場合は、以下のコマンドでログを確認できます：

```bash
docker-compose -f docker/docker-compose.test.yml logs
```

### テストの失敗

テストが失敗した場合は、以下を確認してください：

1. 環境変数が正しく設定されているか
2. BacklogのAPIキーが有効か
3. 指定したプロジェクトが存在し、アクセス権があるか

### Dockerコンテナの手動クリーンアップ

問題が発生した場合、以下のコマンドでコンテナを強制的に停止できます：

```bash
docker-compose -f docker/docker-compose.test.yml down --remove-orphans
```

## 同期テストのメリット

1. **実行状況の可視性**: テストの各ステップがコンソールに出力されるため、実行状況が明確
2. **デバッグの容易さ**: エラーが発生した場合に、どのステップで失敗したかが明確
3. **安定性の向上**: 同期的な実行により、非同期処理の競合や状態の混乱を防止
4. **タイムアウト制御**: 各APIリクエストに明示的なタイムアウトを設定可能
5. **一貫性のあるテスト実行**: テストが一つずつ順番に実行されるため、結果が一貫性を持つ

## 注意点

- 同期テストは非同期テストよりも実行時間が長くなる可能性があります
- 同期テストと非同期テストは共存可能ですが、別々に実行することをお勧めします
- E2Eテストには有効なBacklog APIキーが必要です
