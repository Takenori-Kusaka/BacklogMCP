# 後方互換性ポリシーと破壊的変更管理のための.clinerules

このルールは、コード互換性維持と変更管理の体系的アプローチを定義し、後方互換性と破壊的変更のための統一的なガイドラインを提供します。チーム全体でこれらの規則に従うことで、安定したソフトウェア開発と長期的なメンテナンスを実現します。

## 基本理念

コードベースの一貫性と互換性を維持することは、持続可能なソフトウェア開発の基盤です。このガイドラインは、既存実装の文脈を尊重しつつ安全な変更管理を行うための枠組みを提供します[2][10]。

## 後方互換性の設計哲学

### 驚き最小の原則（Principle of Least Astonishment）

- 既存APIの入出力仕様を厳格に維持すること[9][11]
- デフォルト値の変更は原則として禁止[10]
- 暗黙的な型変換の挙動を維持すること[1]
- 振る舞いの変更は、ユーザーの期待を裏切らない範囲に限定する[1]
- 新機能追加時も既存機能の振る舞いは変えないこと

```
// 良い例：既存メソッドの振る舞いを維持しながら機能を追加
function processData(data, options = {}) {
  // 既存の処理を維持
  const result = existingProcessing(data);
  
  // 新機能を追加（オプション引数で制御）
  if (options.useNewFeature) {
    return enhanceResult(result);
  }
  
  return result;
}

// 悪い例：既存メソッドの振る舞いを変更
function processData(data) {
  // 既存の挙動を変更した新しい処理
  return newProcessing(data); // 破壊的変更！
}
```

## 変更管理プロセスの実装

### コードコンシステンシーの維持戦略

- 静的解析ツール（ESLint/Prettier等）を利用したスタイル統一[3][5]
- 以下のツールを使用してコード一貫性を確保:
  ```
  {
    "linters": ["eslint", "prettier", "stylelint"],
    "ci": {
      "runOnPush": true,
      "failOnWarning": true
    }
  }
  ```
- イディオマティックな実装パターンをドキュメント化[4]
- ボーイスカウトルール：訪れたコードは改善して去る[7]
- 非推奨APIの利用をビルド段階で検出する仕組みを導入（deprecation lint）[9]

### 破壊的変更の承認フロー

破壊的変更を導入する際は、以下のプロセスに従う:

1. **影響範囲分析**
   - 依存関係マップを作成し、影響を受けるコンポーネントを特定[10][11]
   - 内部・外部の依存関係を文書化

2. **代替案の検証**
   - 非破壊的な変更方法の検討を最優先する[11]
   - 新旧API並行運用の可能性を評価

3. **ステークホルダー承認**
   - 以下の関係者から承認を得ること:
     - セキュリティチーム
     - QAチーム
     - プロダクトオーナー
     - アーキテクト
   - 承認記録を保持する

4. **移行計画策定**
   - 明確なタイムラインを設定（推奨: 非推奨期間2年間）[11]
   - 段階的ロールアウト計画
   - モニタリング指標の設定

### 破壊的変更の条件

以下のケースのみ破壊的変更が検討可能:

- セキュリティ上の重大な問題解決のため
- 主要な設計欠陥の修正のため
- パフォーマンス上の著しい改善が見込まれる場合
- 技術的負債の蓄積が臨界点を超えた場合
- 外部依存の重大な変更への対応が必要な場合

## 技術的負債管理のベストプラクティス

### リファクタリングの安全網構築

- スナップショットテスト（Jest/Vitest）による挙動維持確認
  ```javascript
  // スナップショットテストの例
  it('renders component correctly', () => {
    const tree = renderer.create().toJSON();
    expect(tree).toMatchSnapshot();
  });
  ```
- リファクタリング専用ブランチの分離（Git Flow拡張モデル）[8]
- CI環境でのレガシーシステム互換性チェック[5]
- Canaryリリースとモニタリングによる早期問題検出[11]

### 非推奨化プロセスの標準化

機能廃止には三段階移行期間を設定:

1. **警告段階** (6ヶ月)
   - ログ出力による警告
   - ドキュメント更新
   - `@deprecated`タグによるコード内マーキング

2. **代替機能提供** (12ヶ月)
   - 新APIの安定版リリース
   - 移行ガイドの提供
   - 移行スクリプトの提供（可能な場合）

3. **完全削除**
   - メジャーバージョンアップ時にのみ実施[8]
   - 事前告知を十分に行う
   - 移行状況の確認

```javascript
/**
 * @deprecated この関数は v3.0.0 で削除予定です。代わりに newFunction() を使用してください。
 */
function oldFunction() {
  console.warn('警告: oldFunction は非推奨です。代わりに newFunction を使用してください');
  return newFunction();
}
```

## 組織文化の醸成手法

### ソフトウェアクラフトマンシップの実践

- ペアプログラミングによる知識伝承[6]
- コードカタの定期実施（設計パターンの体得）
- テックトークでの失敗事例共有[6]
- 業務時間の10%を技術的負債解消に充てる「10%改善ルール」

### メトリクスに基づく品質管理

- 循環的複雑度（Cyclomatic Complexity）の可視化と閾値設定[3]
  ```json
  {
    "metrics": {
      "complexity": {
        "threshold": 10,
        "action": "warn"
      }
    }
  }
  ```
- 技術的負債指数（TDI）の定量化とトラッキング[5]
- 変更失敗率（Change Fail Rate）のモニタリングと改善[10]
- APIバージョンごとのエラー率ダッシュボード化[11]

## 具体的なコーディングガイドライン

### APIデザイン原則

- 必須パラメータの追加は破壊的変更とみなす[10]
- 新しいパラメータには常にデフォルト値を設定する
- レスポンス構造の拡張は後方互換性を維持する形で行う
- エラーコードの変更・削除は破壊的変更とみなす
- 非公開APIも同様のバージョン管理を行う

```javascript
// 良い例：オプション引数の追加
function fetchData(id, { includeDetails = false, version = 'v1' } = {}) {
  // 実装...
}

// 悪い例：必須引数の追加
function fetchData(id, options) { // 破壊的変更！
  if (!options) throw new Error('options is required');
  // 実装...
}
```

### バージョン管理と移行支援

- 必要に応じてアダプターパターンを使用して互換性を保つ
- ポリフィルを提供して新旧環境での一貫した動作を確保
- 自動移行ツールと詳細なガイドを提供
- ブランチ戦略は安定版と開発版を明確に区分
- APIゲートウェイを使用した複数バージョン並行提供[11]

## 結論：持続可能な開発のための統合ポリシー

このガイドラインは**後方互換性ポリシー**と**破壊的変更管理フレームワーク**を統合した「持続的互換性管理規約」です。

| 要素 | 実施内容 | 主要ツール |
|------|---------|------------|
| 設計原則 | POLA準拠・SemVer採用 | 静的解析ツール |
| 変更管理 | 多段階承認フロー | CI/CDパイプライン |
| 品質保証 | リファクタリング安全網 | テスト自動化 |
| 組織文化 | クラフトマンシップ醸成 | ナレッジ共有 |

プロジェクト規模に応じた段階的導入を推奨:
- スタートアップ段階：「ボーイスカウトルール」の徹底[7]
- 成長段階：セマンティックバージョニングの導入[8]
- 企業規模：変更管理委員会の設置と多段階承認プロセス[10]

Citations:
[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/14398558/1453113b-c48f-4c89-bc1e-2df12b22f227/paste.txt
[2] https://zenn.dev/berry_blog/articles/c72564d4d89926
[3] https://note.com/unikoukokun/n/n3977a603633c
[4] https://zenn.dev/kimkiyong/scraps/7ffcc90b52d35e
[5] https://zenn.dev/aldagram_tech/articles/alda-clinerules
[6] https://github.com/cline/cline/blob/main/.clinerules
[7] https://zenn.dev/watany/articles/50665ee40f4948
[8] https://qiita.com/tomada/items/635c2964f011af89b08c
[9] https://github.com/cline/cline/discussions/622
[10] https://www.issoh.co.jp/tech/details/6033/
[11] https://publish.obsidian.md/aixplore/AI+Development+&+Agents/mastering-clinerules-configuration

---
Perplexity の Eliot より: pplx.ai/share