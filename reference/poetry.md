# Poetry CLIの完全ガイド

Poetryは、Pythonの依存関係管理とパッケージングのためのツールです。このレポートでは、Poetry CLIの仕様と主要コマンドについて詳しくまとめます。

## 基本的な使い方

Poetryのコマンドラインインターフェイスを使うには、単純に`poetry`と入力することですべての利用可能なコマンドのリストを表示できます。特定のコマンドについてのヘルプを見るには、`--help`オプションを使用します[2]。

## グローバルオプション

どのコマンドでも使用できる共通オプションとして、以下のものがあります[2][6]：

- `--verbose (-v|vv|vvv)`: メッセージの詳細レベルを上げる
- `--help (-h)`: ヘルプ情報を表示
- `--quiet (-q)`: メッセージを出力しない
- `--ansi`: ANSI出力を強制する
- `--no-ansi`: ANSI出力を無効にする
- `--version (-V)`: アプリケーションのバージョンを表示
- `--no-interaction (-n)`: 対話的な質問をしない
- `--no-plugins`: プラグインを無効にする
- `--no-cache`: Poetryのソースキャッシュを無効にする
- `--directory=DIRECTORY (-C)`: Poetryコマンドの作業ディレクトリを指定
- `--project=PROJECT (-P)`: プロジェクトルートとして別のパスを指定

## プロジェクト作成・初期化

### new

新しいPythonプロジェクトを作成するコマンドです。デフォルトでは`src`レイアウトが選択されます[6][9]。

```
poetry new my-package
```

#### 主要オプション
- `--name`: パッケージ名を設定
- `--flat`: フラットレイアウトを使用
- `--src`: srcフォルダを使用（デフォルト）
- `--interactive (-i)`: プロジェクト設定を対話的に指定[2]

### init

既存のプロジェクトに`pyproject.toml`ファイルを作成するコマンドです[6][9]。

```
poetry init
```

#### 主要オプション
- `--name`: パッケージ名
- `--description`: パッケージの説明
- `--author`: パッケージの作者
- `--python`: 互換性のあるPythonバージョン
- `--dependency`: バージョン制約付きで必要なパッケージを指定[2]

## 依存関係管理

### add

必要なパッケージを`pyproject.toml`に追加しインストールします[6][8][9]。

```
poetry add requests pendulum
```

バージョン制約の指定も可能です：

```
poetry add pendulum@^2.0.5
poetry add "pendulum>=2.0.5"
poetry add pendulum==2.0.5
```

#### 主要オプション
- `--group (-G)`: 追加する依存関係グループを指定
- `--dev (-D)`: 開発依存関係として追加（`-G dev`のショートカット）
- `--editable (-e)`: 編集可能モードで追加
- `--extras (-E)`: 依存関係に対してアクティブ化するエクストラ[2]

### remove

インストール済みパッケージリストからパッケージを削除します[6][9]。

```
poetry remove pendulum
```

#### 主要オプション
- `--group (-G)`: 依存関係を削除するグループを指定
- `--dev (-D)`: 開発依存関係から削除[2]

### update

依存関係の最新バージョンを取得し、`poetry.lock`ファイルを更新します[6][9]。

```
poetry update
```

特定のパッケージのみを更新することも可能です：

```
poetry update requests toml
```

#### 主要オプション
- `--without`: 無視する依存関係グループ
- `--with`: 含める依存関係グループ
- `--only`: 特定の依存関係グループのみを含める
- `--dry-run`: 実行せずに操作を出力[2]

## 環境管理

### install

`pyproject.toml`ファイルを読み込み、依存関係を解決してインストールします[6][9]。

```
poetry install
```

#### 主要オプション
- `--without`: 無視する依存関係グループ
- `--with`: 含める依存関係グループ
- `--only`: 特定の依存関係グループのみを含める
- `--only-root`: ルートプロジェクトのみをインストール
- `--no-root`: ルートパッケージをインストールしない
- `--extras (-E)`: インストールする機能[2]

### sync

プロジェクトの環境が`poetry.lock`ファイルと同期していることを確認します。`poetry install`と似ていますが、ロックファイルで追跡されていないパッケージも削除します[2][6]。

```
poetry sync
```

#### 主要オプション
- `--without`: 無視する依存関係グループ
- `--with`: 含める依存関係グループ
- `--only`: 特定の依存関係グループのみを含める
- `--no-root`: ルートパッケージをインストールしない[2]

## 情報表示と確認

### show

利用可能なパッケージを一覧表示します[6][9]。

```
poetry show
```

特定のパッケージの詳細を表示することもできます：

```
poetry show pendulum
```

#### 主要オプション
- `--tree`: 依存関係をツリーとして表示
- `--latest (-l)`: 最新バージョンを表示
- `--outdated (-o)`: 古くなったパッケージの最新バージョンを表示[2]

### check

`pyproject.toml`ファイルの内容と`poetry.lock`ファイルとの整合性を検証します[2][6]。

```
poetry check
```

#### 主要オプション
- `--lock`: 現在の`pyproject.toml`に対して`poetry.lock`が存在することを確認
- `--strict`: 警告がある場合に失敗[2]

## パッケージビルドと公開

### build

ソースとホイールアーカイブをビルドします[6]。

```
poetry build
```

#### 主要オプション
- `--format (-f)`: フォーマットを`wheel`または`sdist`に限定
- `--clean`: ビルド前に出力ディレクトリをクリーン[2]

### publish

`build`コマンドでビルドしたパッケージをリモートリポジトリに公開します[6]。

```
poetry publish
```

#### 主要オプション
- `--repository (-r)`: パッケージを登録するリポジトリ
- `--username (-u)`: リポジトリにアクセスするためのユーザー名
- `--password (-p)`: リポジトリにアクセスするためのパスワード
- `--build`: 公開前にパッケージをビルド[2]

## その他の便利なコマンド

### run

プロジェクトの仮想環境内で指定されたコマンドを実行します[6][9]。

```
poetry run python -V
```

`pyproject.toml`で定義されたスクリプトを実行することもできます[2]。

### config

Poetry設定とリポジトリを編集できます[2][6]。

```
poetry config --list
```

### cache

Poetryのキャッシュと対話するためのサブコマンドをグループ化します[2][6]。

### self

Poetry自体のインストールを管理するためのサブコマンドをグループ化します[2][6]。

## まとめ

Poetryは、Pythonプロジェクトの依存関係管理とパッケージングを簡素化する強力なツールです。このドキュメントで説明した様々なコマンドとオプションを使用することで、Pythonプロジェクトの作成から公開までの全プロセスを効率的に管理できます。

仮想環境の管理、依存関係の追加・削除・更新、パッケージのビルドと公開など、Poetryは従来のPythonツールチェーンの複雑さを大幅に削減し、一貫した開発体験を提供します。

Citations:
[1] https://python-poetry.org/docs/cli/
[2] https://python-poetry.org/docs/cli/
[3] https://dev.to/bowmanjd/build-a-command-line-interface-with-python-poetry-and-click-1f5k
[4] https://dev.to/bowmanjd/build-command-line-tools-with-python-poetry-4mnc
[5] https://cocoatomo.github.io/poetry-ja/cli/
[6] https://python-poetry.org/docs/1.8/cli/
[7] https://cocoatomo.github.io/poetry-ja/
[8] https://qiita.com/idenrai/items/80ea6ccc31922d898957
[9] https://blog.ue-y.me/poetry-command/
[10] https://python-poetry.org/docs/
[11] https://qiita.com/mykysyk@github/items/5f08658d0ca2f1c6b32a
[12] https://zenn.dev/wtkn25/articles/python-poetry
[13] https://www.communitylit.org/ppc-overview
[14] https://zenn.dev/atu4403/articles/b776a9f2b7a516d195d1
[15] https://github.com/python-poetry/poetry/blob/main/docs/basic-usage.md
[16] https://realpython.com/videos/managing-dependencies-poetry-overview/
[17] https://stackoverflow.com/questions/73047834/executing-custom-commands-in-python-project-using-poetry
[18] https://qiita.com/kenji-kondo/items/dfe1120dd99489a81f63
[19] https://github.com/python-poetry/poetry/issues/5050
[20] https://zenn.dev/atu4403/articles/python_fire_2022
[21] https://zenn.dev/yamaday/scraps/51008245130dac

---
Perplexity の Eliot より: pplx.ai/share