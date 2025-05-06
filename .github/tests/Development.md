## actによるGitHub Actionsローカルテスト設計書

### 概要

**act**は、GitHub Actionsのワークフロー（`.github/workflows/`配下のYAMLファイル）をローカル環境で実行・デバッグできるCLIツールです。Dockerコンテナを用いてGitHub Actionsの実行環境を再現し、クラウドへプッシュすることなく動作確認が可能です[2][3][4][5][6][7][8][10][13][14][15]。

---

### 前提条件

- Dockerがインストール・起動済みであること
- テストしたいリポジトリのルートディレクトリに`.github/workflows/`が存在すること

---

### インストール手順

1. **Dockerのセットアップ**
   - Docker Desktopなどをインストールし、起動しておく

2. **actのインストール**
   - Homebrew（macOS/Linux）
     ```bash
     brew install act
     ```
   - シェルスクリプト（全OS共通）
     ```bash
     curl https://raw.githubusercontent.com/nektos/act/master/install.sh | bash
     ```
   - Windowsの場合は公式リリースからバイナリをダウンロード[5][7][13][14][15]

---

### 基本的な使い方

1. **リポジトリルートに移動**
   ```bash
   cd 
   ```

2. **ワークフローの実行**
   - デフォルト（`on: push`）イベントのワークフローを実行
     ```bash
     act
     ```
   - 特定イベントで実行（例：pull_request）
     ```bash
     act pull_request
     ```
   - 特定ジョブのみ実行
     ```bash
     act -j 
     ```
   - workflow_dispatchイベントをトリガーし、入力値を渡す
     ```bash
     act workflow_dispatch --input key=value
     ```
   - DryRun（実際には実行せず、何が実行されるか確認）
     ```bash
     act -n
     ```
   - 詳細ログ表示
     ```bash
     act -v
     ```
   - 利用可能なワークフローやジョブの一覧
     ```bash
     act -l
     act pull_request -l
     ```

---

### オプション・設定

- **シークレットの指定**
  - コマンドラインで指定
    ```bash
    act -s SECRET_KEY=secret_value
    ```
  - ファイルで指定（`.secrets`など）
    ```bash
    act --secret-file .secrets
    ```

- **環境変数の指定**
  - `.env`ファイルを自動参照。別ファイルを使う場合
    ```bash
    act --env-file .env.local
    ```

- **Dockerイメージの指定**
  - デフォルトは軽量イメージ。必要なコマンドが不足する場合はイメージを指定
    ```bash
    act -P ubuntu-latest=nektos/act-environments-ubuntu:18.04
    ```
  - M1/M2 Macの場合はアーキテクチャ指定
    ```bash
    act --container-architecture linux/amd64
    ```

- **設定ファイル**
  - よく使うオプションは`.actrc`や`~/.actrc`に記述可能
    ```
    # .actrc例
    -P ubuntu-latest=nektos/act-environments-ubuntu:18.04
    --secret-file .secrets
    ```

---

### Docker連携

- ワークフロー内でDockerを使う場合、ホストの`/var/run/docker.sock`をバインド
  ```bash
  docker run --rm -it \
    --mount type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock \
     bash
  ```
- act自体はホスト側で実行し、ワークフロー内でdockerコマンドを使う場合のみ上記バインドを利用[4][7][10][15]。

---

### トラブルシューティング・注意点

- デフォルトイメージは最小限のコマンドしか入っていないため、必要なコマンドが不足する場合はイメージを変更[4][7][15]。
- `if:`条件式は`${{ ... }}`で囲む必要あり[4]。
- 一部のGitHub Actions固有機能（例：actions/cache）は完全には再現できない[3][6][8][11]。
- 最終的な動作確認はGitHub本番環境で行うこと[4][5][8]。

---

### サンプルワークフローと実行例

#### 例：YAML

```yaml
name: Sample Workflow
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Hello from act!"
```

#### 例：実行

```bash
act
```

---

### まとめ

**act**を使えば、GitHub Actionsのワークフロー開発・デバッグをローカルで迅速に繰り返せます。Dockerベースであるため、実際のGitHub Actionsに近い動作環境を再現できますが、完全な互換性はないため、最終確認はGitHub上で行うことが推奨されます[3][4][5][6][7][8][10][13][14][15]。

Citations:
[1] https://zenn.dev/rescuenow/articles/db176ea5fe2c92
[2] https://zenn.dev/cozy07/articles/77b9422fa90c29
[3] https://qiita.com/kaminuma/items/37838dd31aca91944453
[4] https://vlike-vlife.netlify.app/posts/testtool_act
[5] https://book.st-hakky.com/hakky/github-actions-act/
[6] https://apidog.com/jp/blog/how-to-run-your-github-actions-locally-a-comprehensive-guide-jp/
[7] https://zenn.dev/the_exile/articles/41026a0b317e28
[8] https://qiita.com/coitate/items/030f5c443c6468fa5e67
[9] https://qiita.com/raki/items/4dc1edf24bc1d54191d7
[10] https://qiita.com/eno49conan/items/f4c272c650b546bd96a6
[11] https://apidog.com/jp/blog/how-to-run-your-github-actions-locally-a-comprehensive-guide/
[12] https://docs.github.com/ja/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/manually-running-a-workflow
[13] https://dev.classmethod.jp/articles/act-for-github-actions-local-execution-tool/
[14] https://graff-it-i.com/2025/03/23/post-1595/
[15] https://ikuma-t.com/blog/try-act/
[16] https://dev.classmethod.jp/articles/hands-on-with-github-actions-automate-tasks/

---
Perplexity の Eliot より: pplx.ai/share