# BacklogMCP

BacklogMCPは、Backlog SaaSをModel Context Protocol (MCP)経由で操作できるようにするプロジェクトです。生成AIモデルがBacklogの機能やデータに簡単にアクセスできるようになり、タスク管理、課題追跡、プロジェクト管理などの操作を自動化することができます。

## 概要

BacklogMCPは以下の特徴を持っています：

- **MCPサーバー**: BacklogのAPIをMCPプロトコルに変換し、生成AIモデルからのアクセスを可能にします
- **スケーラブルなアーキテクチャ**: AWS Lambda上でホストされ、CloudfrontとAPI Gatewayを組み合わせた高性能な構成
- **FastAPIベース**: FastAPIを使用したMCPサーバーで、RESTful APIとしても利用可能
- **柔軟なデプロイオプション**: AWS Lambda、ローカル環境、ECSなど様々な環境で動作可能
- **コンテナ対応**: DockerfileとDocker Composeによる簡単なセットアップと開発
- **包括的なテスト戦略**: ユニットテスト、結合テスト、E2Eテストなど複数レベルのテスト
- **TDD開発方針**: テストファーストの開発アプローチによる高品質なコード
- **MCP Inspector統合**: MCP Inspectorを使用した自動E2Eテストとレポート生成

## 機能

BacklogMCPは以下のBacklog機能へのアクセスを提供します：

### プロジェクト管理
- プロジェクト一覧の取得
- 特定のプロジェクトの取得

### 課題管理
- 課題一覧の取得（フィルタリング機能付き）
- 課題の作成
- 課題の詳細取得
- 課題の更新
- 課題の削除
- コメントの追加
- コメント一覧の取得

### 一括操作
- 複数課題のステータス一括更新
- 複数課題の担当者一括更新

### マスタデータ管理
- ユーザー一覧の取得
- 優先度一覧の取得
- ステータス一覧の取得
- カテゴリー一覧の取得
- マイルストーン一覧の取得
- 発生バージョン一覧の取得

これらの機能は、MCPのツールとリソースとして公開され、生成AIモデルから簡単にアクセスできます。

## ドキュメント

詳細なドキュメントは以下のファイルを参照してください：

- [ユーザーガイド](docs/USER_GUIDE.md) - セットアップ方法、使用例、APIの使い方など
- [開発者ガイド](docs/DEVELOPER_GUIDE.md) - アーキテクチャ、開発方針、プロジェクト構造など
- [デプロイガイド](docs/DEPLOYMENT.md) - AWS CDKを使用したデプロイ方法
- [CDKデプロイガイド](docs/CDK_DEPLOYMENT_GUIDE.md) - CDKのドライランとデプロイの詳細な手順
- [貢献ガイド](docs/CONTRIBUTING.md) - プロジェクトへの貢献方法
- [Backlogユースケース](BacklogUsecases.md) - Backlogの包括的なユースケース分析
- [同期E2Eテスト](docs/SYNC_E2E_TESTING.md) - 同期的なE2Eテスト実行ガイド
- [MCP Inspectorテスト](docs/MCP_INSPECTOR_TESTING.md) - MCP Inspectorを使用したE2Eテスト実行ガイド

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。
