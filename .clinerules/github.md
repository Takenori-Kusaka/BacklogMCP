# GitHub プロジェクト開発のための包括的な .clinerules ガイド

このドキュメントは、GitHubプロジェクト開発における包括的なベストプラクティスと設定ガイドラインを提供します。GitHub ActionsからPull Request/Issueテンプレート、コードオーナーシップ、リポジトリ設定まで、効率的かつ安全なGitHubプロジェクト開発に必要な全ての要素を網羅しています。

## リポジトリのベストプラクティス

### 命名規則とリポジトリ構造

リポジトリには明確で一貫性のある命名規則を使用してください。これにより、プロジェクトの目的と内容を一目で理解できるようになります[18]。

#### リポジトリ命名ガイドライン

- **プロジェクトまたはチームの接頭辞を使用**: `teamalpha_authentication_service` や `teambravo_data_pipeline`
- **説明的な名前を使用**: `customer_support_ticketing_system` や `machine_learning_model_trainer`
- **技術スタックを含める**: `image_processor_python` や `frontend_react_app`
- **バージョンまたはステータスタグを使用**: `payment_gateway_v2` や `inventory_management_deprecated`
- **特殊文字を避ける**: シンプルな英数字とハイフン/アンダースコアのみを使用[18]

### 基本プラクティス

- **README ファイルを作成する**: プロジェクトの説明、セットアップ手順、使用方法を含めます[1]
- **リポジトリをセキュリティで保護する**: 適切なアクセス制御と権限設定を行います[1]
- **フォークよりもブランチを優先する**: 内部開発にはブランチを使用し、フォークは外部貢献者向けとします[1]
- **機能やバグ修正のためのブランチを作成**: 
  ```
  git branch feature/new-feature
  git branch bugfix/issue-123
  ```


- **定期的に変更をpullおよびpushする**: チームメンバーの作業と同期を保ちます[20]

## コードオーナーシップとレビュー管理

### CODEOWNERSファイルの活用

CODEOWNERSファイルは、コードベースの特定の部分に責任を持つ個人またはチームを指定することで、コードレビュープロセスを効率化します[3]。

#### CODEOWNERSファイルの作成手順

1. リポジトリに `.github` ディレクトリを作成（存在しない場合）
2. このディレクトリ内に `CODEOWNERS` ファイルを作成[3]

#### コードオーナーの定義方法

```
# リポジトリ全体をDevOpsチームに割り当て
* @your-org/devops

# JavaScriptファイルをフロントエンドチームに割り当て
*.js @your-org/frontend

# 特定のディレクトリを特定のチームに割り当て
/docs @your-org/docs
```


### コードレビューのベストプラクティス

- **二要素認証（2FA）を有効にする**: すべてのGitHubユーザーはセキュリティ強化のために2FAを設定すべきです[2]
- **自分のコードに責任を持つ**: CODEOWNERSファイルで自分が責任を持つ領域を明確にします[2]
- **アトミックなPRを提出する**: PRは小さく、1つのバグ修正または機能のみを含めるようにします[2]
- **通知を確実に受け取る**: 新しいリポジトリからの通知を自動的に購読することをお勧めします[2]
- **ブランチの早期削除**: マージ後はブランチをすぐに削除して、リポジトリを整理します[2]

## GitHub Actions

GitHub Actionsは継続的インテグレーション(CI)と継続的デプロイメント(CD)の自動化を可能にします[10]。

### 継続的インテグレーション（CI）ワークフロー例

```yaml
name: Node Continuous Integration

on:
  pull_request:
    branches: [ master ]

jobs:
  test_pull_request:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v1
        with:
          node-version: 12
      - run: npm ci
      - run: npm test
      - run: npm run build
```


### 継続的デプロイメント（CD）のための設定

CD設定は、コードが統合された後、新しい本番コードを自動的にユーザーにリリースする重要なステップです[10]。

### その他の有用なGitHub Actions例

- **リリース時にNPMパッケージを公開する**
- **メールまたはチャット通知を送信する**
- **定期的なタスク（クリーンアップ、スキャンなど）を実行する**[10]

## プルリクエストとIssueテンプレート

### プルリクエストテンプレートの設定

プルリクエストテンプレートにより、貢献者が必要な情報を提供し、レビュープロセスを効率化できます[9]。

#### テンプレート作成手順

- ルートディレクトリに表示するには: `pull_request_template.md` というファイル名を使用します
- `docs` ディレクトリに表示するには: `docs/pull_request_template.md` というファイル名を使用します
- 複数のテンプレートを使用するには: `.github/PULL_REQUEST_TEMPLATE/` サブディレクトリに格納します[9]

### Issueテンプレートの設定

Issueテンプレートは、ユーザーがIssueを報告する際の一貫性を確保し、必要な情報を収集するのに役立ちます[8]。

#### Issueフォームの作成方法

新しいファイルを作成し、`.github/ISSUE_TEMPLATE` フォルダに追加します[8]。

### 組織全体のコミュニティ健全性ファイル

組織は特別な名前の `.github` リポジトリに以下のファイルを追加して、組織全体のデフォルトとして機能させることができます[13]：

- `CONTRIBUTING`
- `SUPPORT`
- `CODE_OF_CONDUCT`
- `ISSUE_TEMPLATE(S)`
- `PULL_REQUEST_TEMPLATE(S)`[13]

## セキュリティのベストプラクティス

### 機密ファイルの保護

以下のファイルは特に注意が必要です：

```
# セキュリティ
## 機密ファイル
以下は読み取りや変更をしないでください：
- .env ファイル
- src/env配下のファイル
- */config/secrets.*
- */*.pem
- APIキー、トークン、認証情報を含むファイル全般
```


### セキュリティプラクティス

- 機密ファイルを絶対にコミットしない
- シークレット情報は環境変数を使用する
- ログや出力に認証情報を含めない[15][16]

## Dependabotの設定

Dependabotは、プロジェクトの依存関係を最新かつ安全な状態に保つために使用します[11]。

### dependabot.ymlの基本設定

```yaml
# 2つのパッケージマネージャーの最小構成を持つ基本的な dependabot.yml ファイル
version: 2
updates:
  # npmのバージョン更新を有効化
  - package-ecosystem: "npm"
    # ルートディレクトリの `package.json` と `lock` ファイルを確認
    directory: "/"
    # 平日毎日npmレジストリの更新をチェック
    schedule:
      interval: "daily"

  # Dockerのバージョン更新を有効化
  - package-ecosystem: "docker"
    # ルートディレクトリの `Dockerfile` を確認
    directory: "/"
    # 週に1回更新をチェック
    schedule:
      interval: "weekly"
```


## GitHub Copilotの設定

GitHub Copilotの設定は、プロジェクトにAIアシスタンスを提供するために重要です[12]。

### 言語ごとのCopilot設定

以下は、特定の言語でのCopilot有効化/無効化の設定例です：

```xml

  
    
      
        
        
        
      
    
  

```


## .clinerulesの活用

.clinerulesはCline AI補助のためのプロジェクト固有の設定ファイルです[15][16]。

### 基本構造

```
## はじめに
このドキュメントは、Clineが開発を行う際のガイドラインをまとめたものです。

## 技術スタック
- 言語: TypeScript
- フレームワーク: Next.js (AppRouter)
- UI: shadcn/ui + Tailwind CSS
- 状態管理: React Hooks
- データベース: PostgreSQL

## コーディングガイドライン
- シンプルで読みやすいコード
- 適切な命名（変数、関数、クラスなど）
- 一つの関数は一つの責務を持つ
- エラーハンドリングを適切に実装
- コメントは必要な箇所にのみ付ける

## コミットメッセージのガイドライン
- feat: 新機能追加 🚀
- fix: バグ修正 🐛
- docs: ドキュメント更新 📚
- style: スタイル調整 💅
- refactor: リファクタリング ♻️
- test: テスト追加・修正 🧪
- chore: 雑務的な変更 🔧
```


### 作業プロセス設定

開発モードやプロセスの定義を明確にすることで、AIアシスタントが適切な支援を提供できるようになります：

```
## 開発モードについて
以下の4つのモードを状況に応じて自動的に切り替えながら開発を行ってください。

| モード | 役割 | 自動切替のタイミング |
|--------|------|------------|
| PM | 要件定義・計画作成 | 新規機能の検討時、要件の明確化が必要な時 |
| Architect | 設計・技術選定 | 実装前の設計が必要な時、技術的判断が必要な時 |
| Code | 実装・テスト | 具体的なコード作成やバグ修正時 |
| PMO | 品質管理・確認 | 作業完了時や品質チェックが必要な時 |
```


## .github ディレクトリ構造のベストプラクティス

効率的なGitHubプロジェクト管理のための.githubディレクトリ構造を以下に示します：

```
.github/
├── ISSUE_TEMPLATE/
│   ├── bug_report.md
│   ├── feature_request.md
│   └── question.md
├── PULL_REQUEST_TEMPLATE/
│   ├── feature.md
│   └── bugfix.md
├── workflows/
│   ├── ci.yml
│   ├── cd.yml
│   └── dependency-review.yml
├── CODEOWNERS
├── dependabot.yml
├── CONTRIBUTING.md
├── SECURITY.md
└── CODE_OF_CONDUCT.md
```

### ディレクトリ構造の明示

.clinerules設定の一部として、プロジェクトのディレクトリ構造を明示することで、AIアシスタントがプロジェクト構造を理解しやすくなります[7][16]。

```
## ディレクトリ構造
- src/ - ソースコード
  - components/ - UIコンポーネント
  - hooks/ - カスタムフック
  - pages/ - ページコンポーネント
  - services/ - APIサービス
  - utils/ - ユーティリティ関数
- tests/ - テストコード
- docs/ - プロジェクトドキュメント
- .github/ - GitHub関連設定
```

## 結論

この.clinerules設定は、GitHubプロジェクト開発における包括的なベストプラクティスを集約しています。リポジトリ管理、コードオーナーシップ、CI/CD、テンプレート、セキュリティ、AIアシスタンスなど、効果的なGitHubプロジェクト開発に必要なあらゆる側面をカバーしています。これらの設定とガイドラインを活用することで、チームは一貫性のある高品質なプロジェクト開発を実現できます。

この.clinerules設定を基盤として、各プロジェクトの特定のニーズに合わせてカスタマイズし、継続的に進化させていくことをお勧めします。効率的な開発プロセス、明確なコミュニケーション、高品質なコード生成のためにこのガイドラインを活用してください。

Citations:
[1] https://docs.github.com/ja/repositories/creating-and-managing-repositories/best-practices-for-repositories
[2] https://www.w3.org/guide/github/best-practices.html
[3] https://dev.to/eunice-js/a-comprehensive-guide-to-codeowners-in-github-22ga
[4] https://github.com/cline/cline/blob/main/.clinerules
[5] https://www.issoh.co.jp/tech/details/6033/
[6] https://zenn.dev/berry_blog/articles/c72564d4d89926
[7] https://publish.obsidian.md/aixplore/AI+Development+&+Agents/mastering-clinerules-configuration
[8] https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository
[9] https://docs.github.com/ja/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
[10] https://fireship.io/lessons/five-useful-github-actions-examples/
[11] https://docs.github.com/ja/code-security/dependabot/working-with-dependabot/dependabot-options-reference
[12] https://docs.github.com/ja/copilot/managing-copilot/configure-personal-settings/configuring-github-copilot-in-your-environment
[13] https://github.blog/changelog/2019-02-21-organization-wide-community-health-files/
[14] https://learn.microsoft.com/ja-jp/training/modules/maintain-secure-repository-github/
[15] https://qiita.com/tomada/items/635c2964f011af89b08c
[16] https://zenn.dev/kimkiyong/scraps/9642c2ef3e08b3
[17] https://qiita.com/to3izo/items/1a0b487af8d3c5867efb
[18] https://dev.to/pwd9000/github-repository-best-practices-23ck
[19] https://docs.github.com/ja/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects
[20] https://www.linkedin.com/pulse/git-repository-best-practices-developers-muhammad-rashid-4le1f
[21] https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features
[22] https://cloud.gov/pages/knowledge-base/repository-best-practices/
[23] https://note.com/unikoukokun/n/n3977a603633c
[24] https://cline-project-guide.vercel.app
[25] https://kakudo.org/blog/cline-day1-diary/
[26] https://qiita.com/tomada/items/635c2964f011af89b08c
[27] https://docs.gitea.com/usage/issue-pull-request-templates
[28] https://dev.classmethod.jp/articles/pull-request-template/
[29] https://zenn.dev/microsoft/articles/github-copilot-custom-instructions
[30] https://avinton.com/academy/vs-code-github-copilot-setup/
[31] https://graphite.dev/guides/how-to-set-up-branch-protection-rules-in-github
[32] https://github.com/cline/cline
[33] https://zenn.dev/tellernovel_inc/articles/cline-zenn-github
[34] https://qiita.com/sigma_devsecops/items/cd420bd54cbbe1c40cc0
[35] https://cline.bot/faq
[36] https://zenn.dev/berry_blog/articles/c72564d4d89926
[37] https://note.com/unikoukokun/n/nc4365a90c32c
[38] https://github.com/cline/cline/blob/main/docs%2Fprompting%2FREADME.md
[39] https://dev.classmethod.jp/articles/cline-context-model-guide/
[40] https://note.ambitiousai.co.jp/n/n23c92ac6d9bc
[41] https://www.issoh.co.jp/tech/details/6033/
[42] https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/manually-creating-a-single-issue-template-for-your-repository
[43] https://zenn.dev/ianchen0419/articles/0799b2f2831909
[44] https://qiita.com/nyamogera/items/3fe6985b45fbd5377184
[45] https://zenn.dev/haru_iida/articles/github_copilot_ansible
[46] https://www.mitsuru-takahashi.net/blog/github-copilot/
[47] https://qiita.com/masakinihirota/items/0e58a6b921e4420a2882
[48] https://jp.linkedin.com/learning/practical-github-copilot-23091337/4229118
[49] https://code.visualstudio.com/docs/copilot/reference/copilot-settings
[50] https://searx.github.io/searx/admin/settings.html

---
Perplexity の Eliot より: pplx.ai/share