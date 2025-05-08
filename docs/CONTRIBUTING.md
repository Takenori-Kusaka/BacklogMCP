# BacklogMCP 貢献ガイド

BacklogMCPプロジェクトへの貢献を検討していただき、ありがとうございます。このガイドでは、プロジェクトへの貢献方法について説明します。

## 目次

- [行動規範](#行動規範)
- [貢献の種類](#貢献の種類)
- [開発環境のセットアップ](#開発環境のセットアップ)
- [コーディング規約](#コーディング規約)
- [テスト](#テスト)
- [プルリクエストの作成](#プルリクエストの作成)
- [レビュープロセス](#レビュープロセス)
- [リリースプロセス](#リリースプロセス)

## 行動規範

このプロジェクトでは、オープンで友好的な環境を維持するために、以下の行動規範を採用しています：

- 他の貢献者に対して敬意を持って接する
- 建設的なフィードバックを提供する
- 異なる意見や視点を受け入れる
- プロジェクトの目標と方向性を尊重する

## 貢献の種類

プロジェクトへの貢献には、以下のような種類があります：

- **バグ報告**: GitHubのIssueを使用して、バグを報告する
- **機能リクエスト**: GitHubのIssueを使用して、新機能を提案する
- **コード貢献**: プルリクエストを作成して、コードを貢献する
- **ドキュメント改善**: ドキュメントの誤りを修正したり、新しいドキュメントを追加する
- **テスト追加**: 既存の機能に対するテストを追加する
- **レビュー**: 他の貢献者のプルリクエストをレビューする

## 開発環境のセットアップ

### 前提条件

- Python 3.10以上
- Poetry
- Docker（オプション）
- AWS CDK（オプション）

### セットアップ手順

1. **リポジトリのフォークとクローン**

```bash
# GitHubでリポジトリをフォーク
# フォークしたリポジトリをクローン
git clone https://github.com/yourusername/BacklogMCP.git
cd BacklogMCP
```

2. **リモートの設定**

```bash
# 元のリポジトリをupstreamとして追加
git remote add upstream https://github.com/originalusername/BacklogMCP.git
```

3. **依存関係のインストール**

```bash
# Poetryを使用して依存関係をインストール
poetry install
```

4. **環境変数の設定**

```bash
# .env.exampleをコピーして.envを作成
cp .env.example .env
# .envファイルを編集して必要な情報を入力
```

5. **開発サーバーの起動**

```bash
# 仮想環境の有効化
poetry shell

# 開発サーバーの起動
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## コーディング規約

### Pythonコーディング規約

- **PEP 8**: Pythonの標準的なコーディング規約に従う
- **Black**: コードフォーマッターとしてBlackを使用
- **isort**: インポート文の整理にisortを使用
- **flake8**: コードの静的解析にflake8を使用
- **mypy**: 型チェックにmypyを使用

### コミットメッセージ規約

- **Conventional Commits**: コミットメッセージは[Conventional Commits](https://www.conventionalcommits.org/)の形式に従う
  - `feat`: 新機能
  - `fix`: バグ修正
  - `docs`: ドキュメントのみの変更
  - `style`: コードの意味に影響を与えない変更（空白、フォーマット、セミコロンの欠落など）
  - `refactor`: バグ修正でも新機能の追加でもないコードの変更
  - `perf`: パフォーマンスを向上させるコードの変更
  - `test`: 不足しているテストの追加や既存のテストの修正
  - `chore`: ビルドプロセスやドキュメント生成などの変更

### コードスタイルの適用

コードスタイルを適用するには、以下のコマンドを実行します：

```bash
# Blackを使用してコードをフォーマット
black app tests

# isortを使用してインポート文を整理
isort app tests

# flake8を使用してコードを静的解析
flake8 app tests

# mypyを使用して型チェック
mypy app tests
```

## テスト

### テスト戦略

BacklogMCPは、以下の6つのレベルでテストを実施します：

1. **Unitテスト**: 個々の関数やメソッドが期待通りに動作することを確認
2. **結合テスト**: 複数のコンポーネントが連携して正しく動作することを確認
3. **E2Eテスト**: システム全体が実際の環境に近い状態で正しく動作することを確認
4. **デプロイテスト**: コンテナ化された環境でシステムが正しく動作することを確認
5. **CIテスト**: コードの変更がマージされる前に、自動的にテストを実行して品質を確保
6. **CDテスト**: デプロイされた環境が正しく動作することを確認

詳細なテスト戦略については、[tests/TEST_STRATEGY.md](../tests/TEST_STRATEGY.md)を参照してください。

### テストの実行

テストを実行するには、以下のコマンドを実行します：

```bash
# すべてのテストを実行
pytest

# 特定のテストレベルを実行
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# カバレッジレポートを生成
pytest --cov=app

# テスト実行スクリプトを使用
python scripts/run_tests.py --unit      # ユニットテストのみ実行
python scripts/run_tests.py --integration  # 統合テストのみ実行
python scripts/run_tests.py --e2e       # E2Eテストのみ実行
python scripts/run_tests.py --coverage   # カバレッジレポートを生成
python scripts/run_tests.py --verbose    # 詳細な出力
```

### TDD開発方針

BacklogMCPでは、テストファースト（テスト→実装→リファクタ）の開発アプローチを採用しています。新機能や修正を実装する前に、まずテストを作成してください。

## プルリクエストの作成

### ブランチ戦略

- **main**: 安定版のコードを含むブランチ
- **develop**: 開発中のコードを含むブランチ
- **feature/xxx**: 新機能の開発用ブランチ
- **fix/xxx**: バグ修正用ブランチ
- **docs/xxx**: ドキュメント更新用ブランチ
- **refactor/xxx**: リファクタリング用ブランチ

### プルリクエストの手順

1. **最新のdevelopブランチを取得**

```bash
git checkout develop
git pull upstream develop
```

2. **新しいブランチを作成**

```bash
git checkout -b feature/new-feature
```

3. **変更を実装**

```bash
# コードの変更を実装
# テストを追加
# ドキュメントを更新
```

4. **変更をコミット**

```bash
git add .
git commit -m "feat: add new feature"
```

5. **変更をプッシュ**

```bash
git push origin feature/new-feature
```

6. **プルリクエストを作成**

GitHubのウェブインターフェースを使用して、プルリクエストを作成します。プルリクエストには、以下の情報を含めてください：

- プルリクエストのタイトル（Conventional Commitsの形式に従う）
- 変更内容の説明
- 関連するIssueへの参照
- テスト結果
- スクリーンショットや動画（UIの変更がある場合）

### プルリクエストのチェックリスト

プルリクエストを作成する前に、以下のチェックリストを確認してください：

- [ ] コードがコーディング規約に従っている
- [ ] 新しいテストが追加されている
- [ ] すべてのテストが通過している
- [ ] ドキュメントが更新されている
- [ ] コミットメッセージがConventional Commitsの形式に従っている
- [ ] 変更内容が明確に説明されている
- [ ] 関連するIssueへの参照がある

## レビュープロセス

### レビューの流れ

1. プルリクエストが作成されると、自動的にCIテストが実行されます
2. CIテストが通過したら、レビューアーがコードをレビューします
3. レビューアーがコメントを残し、必要に応じて変更を要求します
4. 変更が要求された場合は、変更を実装してプッシュします
5. すべてのレビューコメントが解決され、レビューアーが承認したら、プルリクエストがマージされます

### レビューのガイドライン

- レビューは建設的で敬意を持って行う
- コードの品質、テストの網羅性、ドキュメントの正確性に焦点を当てる
- 具体的なフィードバックを提供する
- 変更が必要な場合は、その理由を説明する
- 良い点も指摘する

## リリースプロセス

### バージョニング

BacklogMCPは、[セマンティックバージョニング](https://semver.org/)を採用しています：

- **メジャーバージョン**: 後方互換性のない変更
- **マイナーバージョン**: 後方互換性のある機能追加
- **パッチバージョン**: 後方互換性のあるバグ修正

### リリースの手順

1. **リリースブランチの作成**

```bash
git checkout develop
git pull upstream develop
git checkout -b release/vX.Y.Z
```

2. **バージョン番号の更新**

```bash
# pyproject.tomlのバージョン番号を更新
# CHANGELOGを更新
```

3. **リリースブランチをプッシュ**

```bash
git add .
git commit -m "chore: bump version to vX.Y.Z"
git push origin release/vX.Y.Z
```

4. **リリースプルリクエストの作成**

GitHubのウェブインターフェースを使用して、`release/vX.Y.Z`から`main`へのプルリクエストを作成します。

5. **リリースプルリクエストのマージ**

レビューとCIテストが通過したら、リリースプルリクエストをマージします。

6. **タグの作成**

```bash
git checkout main
git pull upstream main
git tag vX.Y.Z
git push upstream vX.Y.Z
```

7. **リリースノートの作成**

GitHubのウェブインターフェースを使用して、タグからリリースを作成し、リリースノートを追加します。

8. **developブランチの更新**

```bash
git checkout develop
git pull upstream develop
git merge main
git push upstream develop
```

## 質問と支援

質問や支援が必要な場合は、以下の方法で連絡してください：

- GitHubのIssueを作成する
- プロジェクトのメンテナーに連絡する

プロジェクトへの貢献を検討していただき、ありがとうございます！
