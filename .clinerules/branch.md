# GitHub Flowブランチ戦略のための.clinerules

このドキュメントは、GitHub Flowブランチ戦略を採用したプロジェクトのためのClineルールを定義します。AIアシスタントがコード生成やプロジェクト支援を行う際の指針となります。

## GitHub Flowの基本概念

GitHub Flowは、シンプルで軽量なブランチベースのワークフローです。以下の基本原則に従って運用します[1][2][17]：

- メインブランチ（main/master）は常にデプロイ可能な状態を維持する
- 新機能やバグ修正はfeatureブランチを作成して開発する
- プルリクエストを通じてコードレビューを行う
- レビュー完了後にメインブランチへマージする
- マージ後は即時デプロイを行う

```
【基本フロー図】
main/master (常にデプロイ可能) ─────────────────────────────────────────>
    │                               ↑
    └── feature/xxx ─────────────────┘
        (プルリクエスト・レビュー・マージ)
```

## ブランチ戦略詳細

### メインブランチ（main/master）

メインブランチは以下の特性を持ちます[1][4][18]：

- 常に安定して本番環境にリリース可能な状態を維持する
- 直接コミットは行わず、プルリクエストを通してのみ変更を加える
- ブランチ保護を有効にし、レビューなしの変更を防止する
- 各リリースポイントではタグ付けを行う

### フィーチャーブランチ

フィーチャーブランチは作業用の一時的なブランチで、以下のルールに従います[1][13][14]：

- 必ず最新のメインブランチから分岐させる
- 1つの機能や修正に対して1つのブランチを作成する
- 作業完了後はプルリクエストを作成してレビューを依頼する
- レビュー承認後にメインブランチにマージする
- マージ完了後はフィーチャーブランチを削除する

## ブランチの命名規則

以下の命名規則に従ってブランチを作成してください[9][14]：

### カテゴリプレフィックス

ブランチ名は目的を示すプレフィックスで始めます：

- `feature/` - 新機能の開発
- `fix/` - バグ修正
- `hotfix/` - 緊急のバグ修正
- `refactor/` - コードリファクタリング
- `docs/` - ドキュメント関連の変更
- `test/` - テストコードの追加・修正
- `chore/` - その他の雑務的変更

### 命名パターン

```
/
```

### 命名例

```
feature/user-authentication
fix/login-validation-error
docs/api-documentation
refactor/database-queries
```

### 命名のベストプラクティス

- 一貫性のある命名規則を使用する
- わかりやすく具体的な名前をつける
- セパレータとしてハイフン（-）またはスラッシュ（/）を使用する
- 必要に応じて課題管理システムのID（例：`feature/PROJ-123-login-page`）を含める
- 短すぎず長すぎない名前にする（2〜4単語程度が理想的）
- 数字のみの名前は避ける[14]

## Conventional Commitsに基づくコミットメッセージ規約

コミットメッセージには以下の形式を使用します[5][12][16][19]：

```
[optional scope]: 

[optional body]

[optional footer(s)]
```

### コミットタイプ

- `feat`: 新機能の追加
- `fix`: バグの修正
- `docs`: ドキュメントの変更
- `style`: コードスタイルの変更（セミコロンの追加など）
- `refactor`: リファクタリング（機能追加やバグ修正を含まない）
- `perf`: パフォーマンス改善
- `test`: テストの追加・修正
- `build`: ビルドシステムや依存関係の変更
- `ci`: CI/CD設定の変更
- `chore`: その他の雑務的変更

### 破壊的変更を示す方法

破壊的変更（BREAKING CHANGE）がある場合は、以下のいずれかの方法で示します[16][19]：

```
feat!: 破壊的変更を含む機能追加

feat(api)!: APIに破壊的変更を加える

feat: 新機能追加

BREAKING CHANGE: この変更は既存のAPIと互換性がありません
```

### コミットメッセージの例

```
feat(auth): ユーザー認証機能を追加

fix(ui): ナビゲーションバーが正しく表示されない問題を修正

docs: READMEにインストール手順を追加

refactor(api): ユーザーAPI実装をリファクタリング
```

### コミットメッセージのベストプラクティス[6]

- 主題と本文は空行で区切る
- 主題行の末尾にピリオドを付けない
- 主題行は大文字で始める
- 命令形で書く（例: "Fix bug"、"Fixed bug"ではなく）
- 本文は72文字以内で折り返す
- 本文では変更の理由と影響を説明する

## プルリクエスト運用

### プルリクエスト作成のタイミング

- 機能実装またはバグ修正が完了した時点
- 早期フィードバックが必要な場合はドラフトPRを作成

### プルリクエストの内容[3]

- 変更内容の簡潔な要約
- 詳細な説明（必要に応じて）
- 関連する課題へのリンク
- 変更の動機と背景
- 変更の種類（新機能、バグ修正など）
- チェックリスト（テスト実行確認など）

### レビュープロセス

- コードレビューは最低1名以上から承認を得る
- CI/CDパイプラインのテストがすべて成功していることを確認
- レビューコメントに対応する
- 承認後にのみマージを行う

## デプロイメントとリリース

GitHub Flowではメインブランチへのマージ後、即時デプロイを推奨しています[17][18]：

1. フィーチャーブランチの変更をメインブランチにマージする
2. 自動テストを実行して問題がないことを確認する
3. メインブランチから本番環境へデプロイする
4. 必要に応じてリリースタグを付ける

## 高度なブランチ戦略の応用

GitHub Flowは基本的にシンプルですが、以下のような応用も検討できます[11][20]：

### Integrationブランチの活用

特定の機能グループを統合するための一時的なブランチを設けることで、大規模な開発をより管理しやすくできます：

```
main ───────────────────────────────────────────────>
  │                    │
  ├── integration/v2 ──┤
  │    │        │      │
  │    ├────────┘      │
  │                    │
  ├── feature/a ───────┤
  │                    │
  └── feature/b ───────┘
```

### 環境別ブランチの活用

複数の環境を持つプロジェクトでは、環境ごとにブランチを用意することも検討できます：

- `main` - 本番環境
- `staging` - ステージング環境
- `develop` - 開発環境

## プロジェクト管理とのインテグレーション

### 課題管理システムとの連携

- 課題IDをブランチ名に含める（例: `feature/PROJ-123-login-page`）
- コミットメッセージに課題IDを含める（例: `feat: ログイン機能を実装 [PROJ-123]`）
- プルリクエストに関連課題へのリンクを含める

### CI/CDとの連携

- メインブランチへのプッシュ時に自動デプロイパイプラインを実行
- プルリクエスト作成時に自動テスト実行
- コードカバレッジレポートの自動生成

## Cline AI アシスタント設定

Cline AIアシスタントは以下のルールに従ってプロジェクトをサポートします[10]：

```markdown
## モード設定

以下の4つのモードを状況に応じて自動的に切り替えながら開発を行ってください：

| モード | 役割 | 使用タイミング |
|--------|------|--------------|
| PM | 要件定義・計画作成 | 新規機能の検討時、要件の明確化が必要な時 |
| Architect | 設計・技術選定 | 実装前の設計が必要な時、技術的判断が必要な時 |
| Code | 実装・テスト | 具体的なコード作成やバグ修正時 |
| PMO | 品質管理・確認 | 作業完了時や品質チェックが必要な時 |

## GitHub Flow支援ルール

### ブランチ作成サポート

新しいブランチを作成する際は：

1. 最新のmainブランチからの分岐を確認
2. 適切なプレフィックス（feature/、fix/など）の使用を促進
3. 簡潔で明確なブランチ名を提案

### コミットメッセージサポート

コミットメッセージ作成時は：

1. Conventional Commits形式に従った記述を促進
2. 適切なタイプ（feat、fix、docsなど）の使用をガイド
3. 明確で簡潔な説明文を提案

### プルリクエストサポート

プルリクエスト作成時は：

1. 適切なテンプレートの使用を促進
2. レビューポイントの明確化をサポート
3. 関連する課題リファレンスの記載を確認

### コードレビューサポート

コードレビュー時は：

1. ベストプラクティスに基づいたレビューコメントを提案
2. パフォーマンスやセキュリティの観点からの検証をサポート
3. コーディング規約への準拠を確認
```

## ブランチ戦略の比較と選択

GitHub Flowはシンプルですが、他の戦略と比較して正しく選択することが重要です[15][20]：

### GitHub Flow vs Git Flow

| 観点 | GitHub Flow | Git Flow |
|------|------------|----------|
| 複雑さ | シンプル（2種類のブランチ） | 複雑（5種類以上のブランチ） |
| リリースサイクル | 継続的デリバリー向け | 計画的リリース向け |
| 適したプロジェクト | Webアプリケーション、SaaS | バージョン管理が重要なソフトウェア |
| CI/CD親和性 | 非常に高い | 中程度 |
| 学習コスト | 低い | 高い |

### GitLab Flow

GitHub FlowとGit Flowの中間的な戦略で、環境ごとのブランチを追加したモデルです[1]：

```
production ← staging ← main ← feature/xxx
```

## 結論

GitHub Flowは最もシンプルで理解しやすいブランチ戦略の一つですが、その効果を最大限に発揮するには、一貫性のあるブランチ命名規則とコミットメッセージ規約を守ることが重要です[9][14][15]。このドキュメントで定義したルールに従うことで、チーム全体の開発効率を高め、高品質なソフトウェア開発を実現できます。

## 参考文献

- Conventional Commits [5][12][16][19]
- GitHub Flow [1][2][17][18]
- Git ブランチ命名規則 [9][14]
- コミットメッセージガイドライン [6][19]
- ブランチ戦略比較 [15][20]

Citations:
[1] https://qiita.com/yumsn/items/08a9317531781bae4f79
[2] https://qiita.com/trsn_si/items/cfecbf7dff20c64628ea
[3] https://doc.stride3d.net/latest/en/contributors/contribution-workflow/github-pull-request-guidelines.html
[4] https://docs.aws.amazon.com/prescriptive-guidance/latest/choosing-git-branch-approach/branches-in-a-git-hub-flow-strategy.html
[5] https://www.conventionalcommits.org/ja/v1.0.0/
[6] https://gist.github.com/robertpainsi/b632364184e70900af4ab688decf6f53
[7] https://ckeditor.com/docs/ckeditor5/latest/framework/contributing/git-commit-message-convention.html
[8] https://www.atlassian.com/ja/git/tutorials/comparing-workflows/feature-branch-workflow
[9] https://qiita.com/Shoya-Miyata/items/9e5fd99f226c6479409d
[10] https://qiita.com/tomada/items/635c2964f011af89b08c
[11] https://docs.aws.amazon.com/ja_jp/prescriptive-guidance/latest/choosing-git-branch-approach/advantages-and-disadvantages-of-the-git-hub-flow-strategy.html
[12] https://zenn.dev/wakamsha/articles/about-conventional-commits
[13] https://craftquest.io/guides/git/git-workflows/feature-branch-workflow
[14] https://takeda-no-nao.net/programming/git/git-branch-naming-convention/
[15] https://qiita.com/ucan-lab/items/371cdbaa2490817a6e2a
[16] https://www.conventionalcommits.org/en/v1.0.0/
[17] https://tracpath.com/bootcamp/learning_git_github_flow.html
[18] https://docs.github.com/ja/get-started/using-github/github-flow
[19] https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13
[20] https://komatsuna4747.github.io/how-to-use-git/branch-strategy.html
[21] https://www.harness.io/blog/github-flow-vs-git-flow-whats-the-difference
[22] https://zenn.dev/harper/articles/23e99cb6bd2043
[23] https://www.baeldung.com/ops/git-commit-messages
[24] https://www.theserverside.com/video/Follow-these-git-commit-message-guidelines
[25] https://graphite.dev/guides/implement-feature-branch-workflows-github
[26] https://gitprotect.io/blog/git-forking-workflow/
[27] https://www.issoh.co.jp/tech/details/6033/
[28] https://note.com/build_service/n/n57025fb1eb23
[29] https://qiita.com/mi2__user/items/21b29928d7d206387c85
[30] https://tc-tech.co.jp/2023/12/05/conventional-commits%E3%82%92%E7%94%A8%E3%81%84%E3%81%9F%E3%82%B3%E3%83%9F%E3%83%83%E3%83%88%E3%83%A1%E3%83%83%E3%82%BB%E3%83%BC%E3%82%B8%E3%81%AE%E6%A8%99%E6%BA%96%E5%8C%96/
[31] https://ja.confluence.atlassian.com/display/BITBUCKET/Workflow+for+Git+feature+branching
[32] https://help.qlik.com/talend/ja-JP/studio-user-guide/8.0-R2024-12/git-feature-branch-workflow
[33] https://developer.playcanvas.com/ja/user-manual/editor/version-control/branch-workflows/
[34] https://alndaly.github.io/docs/others/Github/forking%20workflow/
[35] https://craftquest.io/guides/git/git-workflows/centralized-workflow
[36] https://github.com/mcasimir/release-flow
[37] https://docs.aws.amazon.com/ja_jp/prescriptive-guidance/latest/choosing-git-branch-approach/branches-in-a-git-hub-flow-strategy.html
[38] https://qiita.com/yousan/items/f0801437644527b00342
[39] https://qiita.com/trsn_si/items/cfecbf7dff20c64628ea

---
Perplexity の Eliot より: pplx.ai/share