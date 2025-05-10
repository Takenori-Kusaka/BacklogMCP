# GitHub Actionsをローカルで実行する：nektos/act導入・利用ガイド

GitHub Actionsのワークフローを開発中、動作確認のたびにリポジトリへコミット・プッシュするのは面倒な作業です。nektos/actを使えば、ローカル環境でワークフローを実行でき、開発効率を大幅に向上させることができます。この資料では、actの導入から実践的な利用方法まで詳しく解説します。

## actとは

actは、GitHub Actionsのワークフローをローカル環境で実行するためのコマンドラインツールです。このツールを使用することで、以下のメリットが得られます：

- GitHubにプッシュすることなく、ワークフローの動作確認ができる[1][2]
- 開発サイクルを高速化し、ワークフローのデバッグを効率的に行える[5]
- コミット履歴を汚さずにテストできる[6]
- タスクランナーとしても利用可能（makeやシェルスクリプトの代替）[5]

actは、プロジェクトの`.github/workflows/`ディレクトリからワークフローファイルを読み取り、Docker APIを使用して必要なイメージをプル・ビルドし、コンテナ内でアクションを実行します[2][13]。

## インストール方法

actは複数の方法でインストールできます。お使いの環境に合わせて選択してください。

### macOS (Homebrew)

```bash
brew install act
```

### Linux (シェルスクリプト)

```bash
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

### Windows (Chocolatey)

```bash
choco install act-cli
```

### その他

各種パッケージマネージャーでもインストール可能です。詳細は[公式リポジトリ](https://github.com/nektos/act)を参照してください[14]。

## 初期設定

### 初回実行時の設定

actを初めて実行すると、使用するDockerイメージのサイズを選択するよう促されます[13]：

- **Large** : +20GB、GitHub Actionsで使用されるほぼ全てのツールを含む（ubuntu-18.04のみ）
- **Medium** : 約500MB、アクションをブートストラップするために必要なツールのみを含む
- **Micro** : 200MB未満、アクションをブートストラップするために必要なNodeJSのみ含む

一般的なワークフローでは「Medium」が推奨されています[13][15]。

選択した設定は`~/.actrc`ファイルに保存され、以下のような内容になります[9]：

```
-P ubuntu-latest=catthehacker/ubuntu:act-latest
-P ubuntu-22.04=catthehacker/ubuntu:act-22.04
-P ubuntu-20.04=catthehacker/ubuntu:act-20.04
-P ubuntu-18.04=catthehacker/ubuntu:act-18.04
```

### M1/M2 Mac向け設定

Apple Silicon搭載のMacでは、アーキテクチャの違いにより追加設定が必要です[12]：

`~/.actrc`に以下の行を追加します：

```
--container-architecture linux/amd64
```

または、エイリアスを設定することも可能です[12]：

```bash
# ~/.zshrcや~/.bashrcに追加
alias act='act --container-architecture linux/amd64'
```

## 基本的な使い方

actの基本的なコマンドは以下の通りです：

### ワークフロー一覧の表示

```bash
act -l
```

これにより、実行可能なワークフローとジョブの一覧が表示されます[6][9]。

### 全ワークフローの実行

```bash
act
```

リポジトリに定義されている全てのワークフローを実行します[2][5]。

### ドライラン（実行シミュレーション）

```bash
act -n
```

実際には実行せず、何が行われるかを確認できます[6][9]。

### 特定のジョブを実行

```bash
act -j 
```

特定のジョブのみを実行します[5][8]。

### 特定のイベントでワークフローを実行

```bash
act 
```

例: `act pull_request`、`act workflow_dispatch`[6]。

## 詳細な設定

### 環境変数の設定

環境変数を設定するには、`.env`ファイルを作成するか、実行時にオプションで指定します[9]：

```bash
# .envファイルを使用する場合
act --env-file .act.env

# コマンドラインで指定する場合
act --env FOO=bar
```

`.env`ファイルの例[9]：

```
FOO=foo
BAR=bar
BAZ=baz
```

### シークレットの設定

GitHub Actionsのシークレットをローカルで使用するには[9]：

```bash
# シークレットファイルを使用する場合
act --secret-file .act.secrets

# コマンドラインで指定する場合
act -s MY_SECRET=something
```

`.act.secrets`ファイルの例[9]：

```
GITHUB_TOKEN=XXXXXXXXXX
```

GitHub Actionsでは自動的に設定される`GITHUB_TOKEN`を利用する場合は、Personal Access Token (PAT)を生成して設定する必要があります[9]。

### 設定ファイル

頻繁に使用するオプションは`~/.actrc`ファイルに記述しておくと便利です[9][12]：

```
-P ubuntu-latest=catthehacker/ubuntu:act-latest
-P ubuntu-22.04=catthehacker/ubuntu:act-22.04
-P ubuntu-20.04=catthehacker/ubuntu:act-20.04
-P ubuntu-18.04=catthehacker/ubuntu:act-18.04
--secret-file .act.secrets
--env-file .act.env
--container-architecture linux/amd64
```

## 実践的な使用例

### コンテナを再利用したテスト

ワークフローの変更を迅速にテストするために、コンテナを再利用できます[5][8]：

```bash
act -r
```

### 詳細なログ出力

詳細なデバッグ情報を表示するには[8]：

```bash
act -v
```

### Docker内でactを実行

Dockerコンテナ内でactを実行する場合は、Docker outside of Docker (DooD)のアプローチを使用します[6]：

```bash
docker run --rm -it \
  --mount type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock \
  debian:buster-slim \
  bash
```

コンテナ内で必要なツールをインストールして、actを実行します。

## 制限と注意点

actを使用する際の主な制限と注意点は以下の通りです：

1. **実行環境の制限**: 現時点では、Ubuntuランナーのみがサポートされており、macOSやWindowsランナーは使用できません[6][9]。

2. **完全な再現ではない**: actはGitHub Actionsを完全に再現するものではありません[9]。

3. **GitHub固有の環境変数**: GitHub特有のコンテキスト（`github.repository`や`github.event.head_commit.message`など）を使用している場合、ローカル実行では問題が生じる可能性があります[8]。

4. **リソース使用量**: 特にLargeイメージを使用する場合、多くのディスク容量（20GB以上）を消費します[13]。

5. **GITHUB_TOKEN**: GitHub Actionsでは自動的に設定される`GITHUB_TOKEN`を、actでは手動で設定する必要があります[9]。

## トラブルシューティング

### M1/M2 Macでの実行エラー

Apple Silicon搭載のMacでは、アーキテクチャの違いにより警告やエラーが発生することがあります。その場合は以下のオプションを指定してください[12]：

```bash
act --container-architecture linux/amd64
```

### コマンドが見つからない

インストール後にactコマンドが見つからない場合は、PATHが正しく設定されているか確認してください[6]。

### Docker関連のエラー

actはDockerを使用するため、以下を確認してください：

- Dockerがインストールされ、起動していること
- 現在のユーザーがDockerを実行する権限を持っていること
- Dockerのディスク容量が十分であること

## まとめ

actを使用することで、GitHub Actionsのワークフローをローカルで迅速にテストでき、開発効率を大幅に向上させることができます。主な利点として：

- プッシュ不要のローカルテスト
- 迅速なフィードバック
- コミット履歴の整理
- 効率的なワークフロー開発

この資料を参考に、actをあなたの開発ワークフローに取り入れてみてください。GitHub Actionsの開発がよりスムーズになるはずです。

## 参考リンク

- 公式リポジトリ: https://github.com/nektos/act
- 公式ドキュメント: https://nektosact.com/

Citations:
[1] https://zenn.dev/cozy07/articles/77b9422fa90c29
[2] https://qiita.com/nakamura0907/items/6887c8b0bc9e335cad88
[3] https://masa-maru.com/ff14-act/
[4] https://eikaiwa.weblio.jp/column/phrases/meaning/act
[5] https://zenn.dev/chot/articles/f7c02e79e1f73b
[6] https://vlike-vlife.netlify.app/posts/testtool_act
[7] https://www.sedia.co.jp/product/act3906/
[8] https://docs.scipy.org/doc/scipy/dev/contributor/using_act.html
[9] https://qiita.com/h_tyokinuhata/items/5c7a8e2f5aafe8905229
[10] https://zenn.dev/yumemi_inc/articles/203779a4eba922
[11] https://qiita.com/Jazuma/items/ecdb62a6d77b60164f69
[12] https://zenn.dev/kuuumo/articles/8cf90d53f62751
[13] https://qiita.com/eno49conan/items/f4c272c650b546bd96a6
[14] https://github.com/nektos/act
[15] https://ikuma-t.com/blog/try-act/
[16] https://apidog.com/jp/blog/how-to-run-your-github-actions-locally-a-comprehensive-guide-jp/
[17] https://qiita.com/coitate/items/030f5c443c6468fa5e67
[18] https://sarachantubuyaki.jp/finalfantasyxiv/how-to-install-act-and-plug-ins/
[19] https://kimini.online/blog/archives/21945
[20] https://nobushiueshi.com/wslgithub-actions%E3%82%92%E3%83%AD%E3%83%BC%E3%82%AB%E3%83%AB%E7%92%B0%E5%A2%83%E3%81%A7%E5%8B%95%E3%81%8B%E3%81%9B%E3%82%8Bact%E3%81%AE%E7%92%B0%E5%A2%83%E6%A7%8B%E7%AF%89%E3%83%A1%E3%83%A2/
[21] https://zenn.dev/chiwawa123/articles/99eb2878bec633
[22] https://toramemoblog.com/act-install
[23] https://nativecamp.net/blog/20230330_act
[24] https://blog.okaryo.studio/20220904-run-github-actions-on-local/
[25] https://gamixor.com/act%E3%81%AE%E5%B0%8E%E5%85%A5%E6%96%B9%E6%B3%95/
[26] https://eow.alc.co.jp/search?q=act
[27] https://vlike-vlife.netlify.app/posts/testtool_act
[28] https://qiita.com/eno49conan/items/f4c272c650b546bd96a6
[29] https://zenn.dev/snowcait/articles/7c9c29b3ae9055
[30] https://www.sedia.co.jp/product/act3915/
[31] https://github.com/nektos/act-docs
[32] https://genzouw.com/entry/2023/05/02/083434/3510/
[33] https://dev.classmethod.jp/articles/auto-generate-toc-on-readme-by-actions/
[34] https://www.smartschool.jp/products/detail.php?product_id=21241
[35] https://nektosact.com
[36] https://github.com/nektos/act-environments
[37] https://github.com/nektos/act/blob/master/README.md
[38] https://search.rakuten.co.jp/search/mall/%E3%82%A2%E3%82%AF%E3%83%86%E3%82%A3%E3%83%95+%E3%83%89%E3%82%AD%E3%83%A5%E3%83%A1%E3%83%B3%E3%83%88%E3%83%9B%E3%83%AB%E3%83%80%E3%83%BC+a4+%E3%83%9B%E3%83%AF%E3%82%A4%E3%83%88+act%EF%BC%8D3906%EF%BC%8D70/
[39] https://nektosact.com/usage/index.html
[40] https://zenn.dev/91works/articles/70c67226028809
[41] https://sat0b.dev/posts/20220415
[42] https://zenn.dev/snowcait/scraps/1700921d507cc7
[43] https://qiita.com/wwalpha/items/6c303dcf04e236238315
[44] https://qiita.com/takmot/items/dbc7f4ca432d85b54645
[45] https://zenn.dev/chot/articles/f7c02e79e1f73b
[46] https://github.com/nektos/act/issues/1972
[47] https://docs.scipy.org/doc/scipy-1.12.0/dev/contributor/using_act.html
[48] https://www.nivr.jeed.go.jp/vr/news/h3iskd0000001npo-att/g11-04.pdf
[49] https://docs.gitea.com/usage/actions/act-runner
[50] https://dev.classmethod.jp/articles/troubleshooting-act-execution-issues-in-rancher-desktop/
[51] https://advancedcombattracker.com/faq.php?id=15
[52] https://cbs-act.com/act-matrix-strength/
[53] https://nektosact.com/usage/runners.html
[54] https://nektosact.com/installation/
[55] https://www.act.org/content/dam/act/unsecured/documents/SDUTroubleshooting-Guide.pdf
[56] https://note.com/mntndk0405/n/n4ed29f3bc150
[57] https://github.com/nektos/act
[58] https://stackoverflow.com/questions/76539861/github-actions-with-act-accessing-a-service-from-inside-a-docker-container
[59] https://toramemoblog.com/act-20240114
[60] https://zenn.dev/cozy07/articles/77b9422fa90c29
[61] https://github.com/nektos/act/issues/279
[62] https://docs.github.com/ja/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions
[63] https://cbs-act.com/act-intro/
[64] https://www.nivr.jeed.go.jp/vr/news/h3iskd0000001r36-att/r6-04.pdf
[65] http://www.seiwa-pb.co.jp/search/bo05/bn1078.html
[66] https://www.jstage.jst.go.jp/article/jabctc/44/0/44_490_2/_pdf/-char/en
[67] https://www.act.gov.au/migration/skilled-migrants/canberra-matrix
[68] https://github.com/ChristopherHX/github-act-runner
[69] https://github.com/nektos/act/issues/1548
[70] https://www.companionlink.com/support/kb/Act!_Sync_Troubleshooting_Guide

---
Perplexity の Eliot より: pplx.ai/share