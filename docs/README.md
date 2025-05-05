# BacklogMCP API ドキュメント

このディレクトリには、BacklogMCP APIのOpenAPI仕様書が含まれています。

## 概要

BacklogMCP APIは、Backlog SaaSをModel Context Protocol (MCP)経由で操作するためのAPIです。
このAPIドキュメントは、GitHub Actionsによって自動的に生成され、GitHub Pagesにデプロイされます。

## ドキュメントの生成方法

OpenAPI仕様書は、以下の手順で生成されます：

1. CIパイプラインでアプリケーションを起動
2. `/openapi.json`エンドポイントからOpenAPI仕様を取得
3. JSON形式からYAML形式に変換
4. RedoclyでHTML形式のドキュメントを生成
5. GitHub Pagesにデプロイ

## ローカルでの確認方法

ローカル環境でAPI仕様書を確認するには、以下の手順を実行してください：

```bash
# アプリケーションを起動
poetry run python -m app.main

# 別のターミナルでOpenAPI仕様書を生成
poetry run python scripts/generate_openapi.py

# 生成されたYAMLファイルを確認
cat docs/openapi.yaml
```

または、アプリケーション起動後にブラウザで以下のURLにアクセスすることでSwagger UIを確認できます：

```
http://localhost:8000/docs
