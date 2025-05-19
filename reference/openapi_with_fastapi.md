# FastAPIでOpenAPI YAMLファイルを出力する方法

FastAPIはPythonベースの高速なWebフレームワークで、自動的にOpenAPI（旧Swagger）ドキュメントを生成する機能を持っています。標準ではJSON形式での出力のみですが、YAML形式でもOpenAPI仕様を出力する方法がいくつか存在します。ここでは、Poetry環境でFastAPIプロジェクトからopenapi.yamlを出力する方法を詳しく解説します。

## FastAPIにおけるOpenAPI生成の基本

FastAPIはPythonの型ヒントを活用して、自動的にAPIドキュメントを生成します。標準では、以下のエンドポイントでSwagger情報にアクセスできます[1]：

- Swagger UI: http://localhost:8000/docs
- Swagger JSON: http://localhost:8000/openapi.json
- ReDoc: http://localhost:8000/redoc

しかし、標準ではYAML形式での出力は備わっていないため、追加の実装が必要です[8]。

## 方法1: app.openapi()を使用したYAMLファイル出力

FastAPIクラスのインスタンスが持つ`openapi()`メソッドを利用して、OpenAPIスキーマをプログラム的に取得し、YAMLに変換して保存する方法です。

### 必要なパッケージのインストール

まず、Poetry環境でPyYAMLをインストールします：

```bash
poetry add PyYAML
```

### YAML出力スクリプトの実装

以下のようなPythonスクリプトを作成します：

```python
import yaml
from your_app import app  # あなたのFastAPIアプリをインポート

def export_openapi_yaml():
    openapi_schema = app.openapi()
    with open("openapi.yaml", "w") as f:
        yaml.dump(openapi_schema, f, sort_keys=False)

if __name__ == "__main__":
    export_openapi_yaml()
    print("OpenAPI YAML exported to openapi.yaml")
```

このスクリプトは、FastAPIアプリケーションからOpenAPIスキーマを取得し、YAMLファイルとして保存します。FastAPIが起動している必要はありません[1]。

## 方法2: YAMLを提供する専用エンドポイントの追加

実行中のFastAPIアプリケーションに新しいエンドポイントを追加して、OpenAPIスキーマをYAML形式で提供する方法です。

```python
from fastapi import FastAPI, Response
from functools import lru_cache
import yaml

def set_openapi_yaml(app: FastAPI) -> None:
    @lru_cache()
    def read_openapi_yaml() -> Response:
        openapi_json = app.openapi()
        yaml_s = yaml.dump(openapi_json, Dumper=yaml.CDumper)
        return Response(yaml_s, media_type="text/yaml")

    app.add_api_route(
        "/openapi.yaml",
        read_openapi_yaml,
        methods=["GET"],
        include_in_schema=False,
    )
```

メインアプリケーションコードで以下のように使用します：

```python
from fastapi import FastAPI

app = FastAPI()
set_openapi_yaml(app)

# 他のルート定義...
```

この実装により、`/openapi.yaml`にGETリクエストを送ることでYAML形式のOpenAPIスキーマを取得できるようになります[8]。`include_in_schema=False`を指定することで、このエンドポイント自体はOpenAPIドキュメントには表示されません。

## 応用例: pyproject.tomlからAPIバージョンを取得

Poetryで管理しているプロジェクトでは、`pyproject.toml`からバージョン情報を読み取り、OpenAPIスキーマに反映させることができます[4]。

まず、必要なパッケージをインストールします：

```bash
poetry add toml
```

そして、カスタムOpenAPIスキーマを生成する関数を実装します：

```python
import os
import toml
from typing import Any, Dict
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    with open("pyproject.toml") as f:
        pyproject_toml = toml.load(f)
    
    poetry: Dict[str, Any] = pyproject_toml["tool"]["poetry"]
    title: str = poetry["name"]
    version: str = poetry["version"]
    description: str = poetry["description"]

    app.openapi_schema = get_openapi(
        title=title,
        version=version,
        description=description,
        routes=app.routes,
    )
    
    return app.openapi_schema

# FastAPIアプリケーションに適用
app = FastAPI()
app.openapi = lambda: custom_openapi(app)
```

このようにすることで、`pyproject.toml`に定義されたバージョン情報がOpenAPIスキーマに反映されます[4]。

## YAMLとJSON両方のOpenAPI仕様を提供する方法

YAML形式とJSON形式の両方でOpenAPI仕様を提供したい場合は、以下のように両方のエンドポイントを設定できます：

```python
from fastapi import FastAPI, Response
import yaml

app = FastAPI()

@app.get("/openapi.yaml", include_in_schema=False)
async def get_openapi_yaml():
    openapi_schema = app.openapi()
    yaml_s = yaml.dump(openapi_schema, Dumper=yaml.CDumper)
    return Response(yaml_s, media_type="text/yaml")

# 既存のJSONフォーマットのエンドポイント (/openapi.json) はデフォルトで使用可能
```

## 出力されたYAMLファイルの活用

出力したOpenAPI YAMLファイルは、以下のように活用できます：

1. APIドキュメントの共有や配布[10]
2. APIクライアントコードの自動生成[3][12]
3. Swagger Editor や Apidog などのツールでの可視化[5]
4. APIテスト自動化ツールでの利用

## まとめ

FastAPIでOpenAPI YAMLファイルを出力するには、主に2つの方法があります：

1. `app.openapi()`メソッドを使用してYAMLファイルを直接生成する方法
2. YAMLを提供する専用エンドポイントを追加する方法

Poetry環境では、必要なパッケージ（PyYAML）をインストールした上で実装し、さらに`pyproject.toml`からバージョン情報を読み取ることで、より統合された管理が可能になります。用途に応じて適切な方法を選択してください。

これらの方法を使えば、FastAPIのコードからOpenAPI YAML仕様を簡単に生成でき、API設計とコードの乖離を防ぎながら、統一されたドキュメントを維持することができます[11]。

Citations:
[1] https://qiita.com/fukutaro/items/0521f45a5aaed7326e76
[2] https://fastapi.tiangolo.com/ja/features/
[3] https://github.com/heiwa4126/fastapi-code-generator-example1
[4] https://qiita.com/que9/items/4c4685f95c507561356d
[5] https://apidog.com/jp/blog/api-document-with-yaml/
[6] https://mojaie.github.io/environment-memo/
[7] https://zenn.dev/horitaka/articles/fastapi-openapi-typescript
[8] https://zenn.dev/oroshi/articles/fastapi_document_customize
[9] https://hotchpotchj37.wordpress.com/2022/08/27/%E7%B6%9A-fastapi-code-generator/
[10] https://qiita.com/papasim824/items/6e3a20cd368452f95330
[11] https://note.com/wa1st_tak/n/nf8742577f721
[12] https://hotchpotchj37.wordpress.com/2022/07/30/%E3%81%AF%E3%81%98%E3%82%81%E3%81%A6%E3%81%AEfast-api%E3%81%8B%E3%82%89%E3%81%AEfastapi-code-generator/
[13] https://stackoverflow.com/questions/63809553/how-to-run-fastapi-application-from-poetry
[14] https://dev.to/dendihandian/trying-poetry-a-new-python-dependency-manager-318k
[15] https://pypi.org/project/PyYAML/
[16] https://qiita.com/SBS_Takumi/items/a44ccc5d645519cf25f8
[17] https://en-ambi.com/itcontents/entry/2023/01/30/093000/
[18] https://gift-tech.co.jp/articles/fastapi-openapi/
[19] https://zenn.dev/collabostyle/articles/e7e3faddc27aff
[20] https://qiita.com/XPT60/items/deac8d6155da58afbb6f
[21] https://github.com/python-poetry/poetry/issues/9266
[22] https://scrawledtechblog.com/docker-fastapi-poetry-requirements-txt/
[23] https://zenn.dev/tellernovel_inc/articles/27e21b8cca94c8
[24] https://pypi.org/project/fastapi-yaml/
[25] https://qiita.com/XPT60/items/aa6cf8443e613c47a984
[26] https://qiita.com/_etoile/items/f63471fa4e21ec5d17ad
[27] https://zenn.dev/takuty/articles/b83c70c32820bb
[28] https://stackoverflow.com/questions/77828411/unable-to-install-pyyaml-using-poetry
[29] https://github.com/python-poetry/poetry/issues/8287
[30] https://github.com/vwxyzjn/cleanrl/issues/418
[31] https://zenn.dev/shotakaha/scraps/9416c30cd7745a
[32] https://qiita.com/ksato9700/items/b893cf1db83605898d8a
[33] https://techblog.recochoku.jp/11733
[34] https://qiita.com/en2enzo2/items/89222e93f97372b1143d

---
Perplexity の Eliot より: pplx.ai/share