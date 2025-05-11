# .clinerules

# 基本的なアクション
notice=すべての実行結果はReadme.mdやdocs/Development.mdなどに記載し、開発の一貫性を担保できるようにし、それらのドキュメントがあれば、新たに参加したほかの開発者が滞りなく開発を始められること
notice=すべての実行は必ずテスト、動作確認を伴って完了とします。自己動作確認はプロとして当たり前のアクションです。以下の手順を遵守してください。
1. やるべきことの確認
2. 事前情報調査(プロジェクト内の各ファイルを参照)
3. 計画立案
4. コード修正
5. コードレビュー
6. テスト実行
7. 動作確認
7.1. 単体テストをcli実行
7.2. 結合テストをcli実行
7.3. e2eテストをcli実行
7.4. github actionsのactによるローカル実行
8. ドキュメント修正

# コードスタイル
notice=PEP8に従ったコードスタイルを遵守すること
notice=型アノテーション(pydanticなど)を必ず記述すること
notice=docstringを必ず記述すること
notice=関数やメソッドの引数には、型アノテーションを必ず記述すること
notice=関数やメソッドの戻り値には、型アノテーションを必ず記述すること
notice=関数やメソッドの引数には、デフォルト値を必ず指定すること

# プロジェクト構造（ルート直下に修正）
allow=app/**
allow=tests/**
allow=scripts/**
allow=.github/**
allow=cdk/**
allow=docker/**

# Poetry関連ファイル
allow=pyproject.toml
allow=poetry.lock
deny=requirements/**

# テスト粒度ごと
allow=tests/unit/**
allow=tests/integration/**
allow=tests/e2e/**

# 許可するファイル形式
allow=**/*.py
allow=**/*.json
allow=**/*.yml
allow=**/*.yaml
allow=**/Dockerfile

# 禁止するファイル形式
deny=**/*.log
deny=**/*.tmp

# その他
allow=README.md
allow=LICENSE

# TDD/CIルール
notice=すべての新規機能・修正はテストファースト（テスト→実装→リファクタ）で行うこと
notice=テストなき実装ファイルのコミットはCIで警告
notice=pytestによる自動テスト・カバレッジ計測をCIで必須化
notice=テストはunit/integration/e2eに分類し、各粒度で必ずテストを作成
notice=FastAPIエンドポイントも必ずテストを作成
notice=テストコードと実装コードは常にペアで管理すること

# Poetry/uv関連ルール
notice=利用するパッケージは可能な限り最新化すること（AIモデルは古いナレッジカットオフのため、推奨パッケージでもバージョンが古い場合があるため、常に最新バージョンを意識する）
notice=依存関係の管理はPoetryを使用すること
notice=パッケージのインストールはuvを使用して高速化すること
notice=pyproject.tomlに全ての依存関係を記述すること
notice=仮想環境はPoetryで管理すること
notice=依存パッケージのバージョン不整合が発生した場合は、FastAPIのバージョンをコアとし、他の依存パッケージ（例：pydantic, uvicorn等）はFastAPIの互換性に合わせて調整すること

# 型チェック・バリデーションルール
notice=すべてのコードは型アノテーションや型チェックを必須とし、型エラーを回避するためにany型や型無視（type: ignore等）を安易に使用してはならない。型安全性を維持すること。

# テスト失敗時の対応ルール
notice=テストで失敗が発生した場合、テストをスキップ（skip）したり、passやassert True等で無意味に通過させるのではなく、テストの意義を確認し、必要に応じて実装やテスト自体を修正し、正しくテストが通る状態にすること。

# コメント
# - 必要に応じて deny ルールを追加してください。
# - CI/CD 用のルールは .github/workflows に記述されています。
# - TDD原則・Pythonテスト自動化の観点を明示
