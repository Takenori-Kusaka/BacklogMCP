# BacklogMCP TDD開発方針・clinerules拡張案

## 推奨プロジェクト構成（TDD）

```
BacklogMCP/
├── app/                  # FastAPIアプリケーション
│   └── main.py           # アプリケーションのエントリーポイント
├── tests/                # テスト（TDDを徹底: unit, integration, e2e）
│   ├── unit/
│   ├── integration/
│   └── e2e/
...
```

## TDD開発方針
- すべての新規機能・修正は「テストファースト」（テスト→実装→リファクタ）
- テストは `tests/unit/`（ユニット）、`tests/integration/`（統合）、`tests/e2e/`（E2E）に分類
- FastAPIのエンドポイントも必ずテストを作成
- pytestを標準とし、カバレッジ計測をCIで必須化

## clinerulesへの反映例
- `allow=tests/unit/**` などテスト粒度ごとに明示
- テストなき実装ファイルのコミットをCIで警告

---
この方針を `.clinerules` に反映し、TDDの原則を守る構成・運用を推奨します。
