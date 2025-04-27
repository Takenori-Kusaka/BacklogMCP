# Model Context Protocol (MCP)：生成AIのための標準連携プロトコル

MCPは、生成AIモデルと外部データソースやツールを標準化された方法で接続するためのオープンプロトコルです。2024年11月にAnthropicが発表し、OpenAIを含む主要企業が採用を始めている次世代の技術標準です。本レポートでは、MCPの基本概念から技術仕様、実装方法まで幅広く解説します。

## MCPとは何か：基本概念と目的

MCPは「Model Context Protocol（モデル・コンテキスト・プロトコル）」の略称で、生成AIが外部のツールやデータソースと簡単につながるための技術規格です[1]。従来、AIに外部システムの機能を利用させるには、システムごとに個別の接続方法（API連携）を開発する必要がありました。MCPはこの課題を解決するために、AIと外部システムの接続方法を標準化しています[1]。

### 「AI界のUSB充電器」としてのMCP

MCPは「AI界のUSB充電器」と表現されることがあります[1]。この比喩が示すように、MCPはAIアプリケーションと外部ツール・データソースの接続を一つの標準で実現します。従来は10個の機能を追加したいなら10個の異なる連携を個別に開発する必要がありましたが、MCPなら一つの標準でそれらすべてを扱えるようになります[1]。

### なぜMCPが生まれたのか

最新のAIモデル自体は高度な能力を持っていますが、最新情報への限定的なアクセスや、特定のシステムとの連携が難しいという制約がありました[1]。MCPは、AIモデルがより多くのデータソースやツールにアクセスできるようにすることで、この問題を解決します[6]。

## MCPのアーキテクチャ

MCPは「ホスト」「クライアント」「サーバー」という3つの主要コンポーネントから構成されています[11][20]。

### ホスト (Host)

LLMアプリケーション（Claude DesktopやIDEなど）で、接続を開始する役割を担います[11][20]。ホストは複数のクライアントを生成・管理し、全体のコントロールを行います[11]。

### クライアント (Client)

ホストアプリケーション内で生成される、サーバーとの1対1の接続を維持する役割です[11][20]。クライアントはサーバーに対してリクエストを送信し、レスポンスを受け取ります[11]。

### サーバー (Server)

クライアントに対して、コンテキスト、ツール、プロンプトを提供する役割です[11][20]。サーバーはリソースやツールを公開し、クライアントからのリクエストに応答します[11]。

### LINE通信に例えるMCPの構造

MCPの構造は、スマホのメッセンジャーアプリLINEに例えることができます[11]：

- ホスト = LINEアプリ本体（MCP ではAI機能を持った中心的存在）
- クライアント = 個々のチャットウィンドウや会話スレッド
- サーバー = 友達やグループなど、メッセージを受け取って返事をする相手

ホストが複数のクライアントを通じて、それぞれ異なるサーバーと通信する構造になっています[11]。

## MCPの技術仕様

### 基本プロトコル

MCPはJSON-RPC 2.0をベースにしたプロトコルを使用しています[4][10][11]。すべての通信は一定のフォーマットに従ったJSONメッセージで行われます。

### メッセージタイプ

MCPでは主に以下のメッセージタイプが使用されます[10][11]：

1. **リクエスト (Request)**：レスポンスを期待するメッセージ。method と必要に応じて params を含む[10]
2. **レスポンス (Response)**：リクエストに対する応答。result または error を含む[10]
3. **通知 (Notification)**：一方向のメッセージ（レスポンスを期待しない）[10]

例えば、ツールを呼び出すリクエストは以下のような形式になります[10]：

```json
{
  "jsonrpc": "2.0",
  "id": 123,
  "method": "tools/call",
  "params": {
    "name": "myTool",
    "arguments": { "arg1": "value" }
  }
}
```

### トランスポート層

MCPは現在、以下の2つの主要なトランスポート方式をサポートしています[10][18]：

1. **stdio（標準入出力）**：主にローカル実行向けで、サーバーがサブプロセスとして実行される場合に使用[10][18]
2. **Streamable HTTP**：HTTP/SSEを介した通信で、リモートサーバー向け[18]

2025年4月時点では、セキュリティ上の理由から多くのMCPクライアントとサーバー間の通信にはstdioが使用されています[18]。

## MCPの主要機能

MCPサーバーは、クライアントに対して以下の機能を提供することができます[11][15]：

### 1. リソース (Resources)

データやコンテキストを提供する機能です[11][15]。リソースはURI（Uniform Resource Identifier）で識別され、クライアントはこれを使用して特定のリソースにアクセスします[15]。

例えば、以下のようなリクエストでリソース一覧を取得できます[15]：

```json
{
  "jsonrpc": "2.0",
  "id": "request-123",
  "method": "resources/list",
  "params": {}
}
```

### 2. ツール (Tools)

AIモデルが実行できる関数です[11][15]。ツールは名前で識別され、引数を受け取って処理を実行し、結果を返します[10]。

### 3. プロンプト (Prompts)

テンプレート化されたメッセージとワークフローを提供します[11]。プロンプトを使用することで、特定のタスクに最適化された指示をAIに提供できます。

## MCPの通信フロー

MCPの基本的な通信フローは以下の通りです[10][11]：

1. **初期化 (Initialize)**：
   - クライアントが `initialize` リクエストを送信し、プロトコルバージョン、機能、クライアント情報を伝える
   - サーバーが選択したプロトコルバージョン、機能、サーバー情報、オプションの指示を返す
   - クライアントが `initialized` 通知を送信して準備完了を確認

2. **メッセージ交換**：
   - リソース一覧の取得 (`resources/list`)
   - 特定リソースの読み取り (`resources/read`)
   - ツール一覧の取得 (`tools/list`)
   - ツールの呼び出し (`tools/call`)
   - プロンプトの取得 (`prompts/get`) など

3. **終了**：
   - トランスポートの終了（stdioの場合はstdinが閉じられるなど）
   - エラー発生時
   - 明示的なシャットダウン

## MCPの実装方法

### TypeScript SDKを使用したMCPサーバーの構築

Anthropicは公式のTypeScript SDKを提供しており、これを使用してMCPサーバーを簡単に構築できます[5][7][16]。以下は簡単なMCPサーバーの実装例です[16]：

```typescript
#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// MCPサーバーの作成
const server = new McpServer({ name: "Demo", version: "1.0.0" });

// ツールの追加
server.tool("add", 
  { a: z.number(), b: z.number() }, 
  async ({ a, b }) => ({ 
    content: [{ type: "text", text: String(a + b) }] 
  })
);

// リソースの追加
server.resource(
  "greeting",
  new ResourceTemplate("greeting://{name}", { list: undefined }),
  async (uri, { name }) => ({
    contents: [{ uri: uri.href, text: `Hello, ${name}!` }]
  })
);

// 標準入出力でサーバーを起動
const transport = new StdioServerTransport();
await server.connect(transport);
```

### MCPクライアントの実装

TypeScript SDKを使用して、MCPクライアントを実装することも可能です[7]：

```typescript
import { Client } from "@modelcontextprotocol/sdk/client";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/transports/stdio";
import { CallToolResultSchema } from "@modelcontextprotocol/sdk/schemas";

// クライアントの初期化
const client = new Client(
  { name: "mcp-typescript test client", version: "0.1.0" },
  { capabilities: { sampling: {} } }
);

// トランスポートの設定
const clientTransport = new StdioClientTransport({
  command: "npx",
  args: ["-y", "@modelcontextprotocol/server-memory"]
});

// サーバーへの接続
await client.connect(clientTransport);

// ツールの呼び出し
const result = await client.request({
  method: "tools/call",
  params: { name: "read_graph", arguments: {} }
}, CallToolResultSchema);
```

## 具体的なMCPサーバーの例

### GitHub MCP Server

GitHub MCP Serverは、AIアシスタントがGitHubリポジトリにアクセスし、操作できるようにするためのサーバーです[8][19]。開発者はこれを使って、コードの分析、イシューの管理、PRのレビューなどをAIに任せることができます[8][19]。

### Filesystem MCP Server

ファイルシステムへのアクセスを提供するMCPサーバーで、AIアシスタントがローカルファイルを読み書きできるようにします[14]。

### Weather MCP Server

天気情報を提供するMCPサーバーの例も紹介されています[16]。OpenWeather APIと連携して、現在の天気や予報をAIに提供します。

## MCPの利点と将来性

### MCPの主なメリット

1. **標準化による開発効率の向上**：共通のプロトコルにより、AIと外部ツールの連携開発が効率化[1]
2. **拡張性の向上**：新しいデータソースやツールを簡単に追加可能[1][6]
3. **セキュリティの確保**：標準化されたアクセス制御により、安全なデータアクセスが可能[6][10]
4. **相互運用性の実現**：異なるAIプラットフォームとツール間の相互運用が容易に[6]

### 今後の発展性

MCPはまだ比較的新しい技術規格ですが、AnthropicやOpenAIなど主要なAI企業が採用を始めており、今後の拡大が期待されています[6][14]。特に、リモートサーバー向けのセキュリティ仕様が整備されれば、クラウドベースのMCPサービスがさらに普及する可能性があります[18]。

## まとめ

Model Context Protocol (MCP)は、生成AIと外部データソース・ツールを標準化された方法で接続するための革新的なプロトコルです。「AI界のUSB充電器」とも例えられるMCPは、AIの活用範囲を大きく広げ、開発者の生産性を向上させる重要な技術となっています[1]。

ホスト・クライアント・サーバーの3層構造と、JSON-RPCベースの通信プロトコルにより、AIアプリケーションは様々なデータソースやツールにシームレスにアクセスできるようになります[11][20]。TypeScript SDKなどの開発ツールも整備されており、比較的容易にMCPサーバーとクライアントを構築できます[5][7][16]。

今後、MCPの普及により、AIアシスタントはさらに多くのコンテキストと機能にアクセスできるようになり、より実用的で価値の高いタスクをこなせるようになるでしょう。企業や開発者は、MCPの可能性を探求し、自社のデータソースやツールをMCPサーバーとして公開することで、AIエコシステムの一部となることができます。

Citations:
[1] https://www.adcal-inc.com/column/mcp/
[2] https://zenn.dev/tmrekk/articles/cce8f478f8b9ac
[3] https://www.union.ai/docs/byoc/deployment/platform-architecture/
[4] https://note.com/npaka/n/n468baea87445
[5] https://github.com/modelcontextprotocol/typescript-sdk
[6] https://www.anthropic.com/news/model-context-protocol
[7] https://zenn.dev/laiso/articles/mcp-typescript-sdk
[8] https://apidog.com/blog/github-mcp-server/
[9] https://modelcontextprotocol.io/specification/2025-03-26
[10] https://github.com/cyanheads/model-context-protocol-resources/blob/main/guides/mcp-server-development-guide.md
[11] https://zenn.dev/mkj/articles/0ed4d02ef3439c
[12] https://rescale.com/ja/blog/rescale-launches-industrys-first-intelligent-control-plane-for-hybrid-and-multi-cloud-big-compute/
[13] https://airbyte.com/data-engineering-resources/data-plane-vs-control-plane
[14] https://openai.github.io/openai-agents-python/mcp/
[15] https://zenn.dev/atamaplus/articles/5bf2bc1acef5b1
[16] https://note.com/npaka/n/n4216cfc51794
[17] https://spec.modelcontextprotocol.io/specification/2024-11-05/basic/transports/
[18] https://azukiazusa.dev/blog/mcp-server-streamable-http-transport
[19] https://zenn.dev/takna/articles/mcp-server-tutorial-05-github
[20] https://modelcontextprotocol.io/docs/concepts/architecture
[21] https://zenn.dev/cloud_ace/articles/model-context-protocol
[22] https://note.com/npaka/n/nfbb9337bf4e9
[23] https://qiita.com/to3izo/items/99dd3cde237c2e5a007f
[24] https://www.itmedia.co.jp/aiplus/articles/2504/07/news106.html
[25] https://techtrends.jp/keywords/model-context-protocol/
[26] https://note.com/wandb_jp/n/n1f174aeed14d
[27] https://docs.netapp.com/ja-jp/netapp-solutions/ai/osrunai_netapp_ontap_ai_and_ai_control_plane.html
[28] https://zenn.dev/skmkzyk/articles/portal-control-data-plane
[29] https://zenn.dev/herp_inc/articles/00917098b3ffd3
[30] https://chatgpt-enterprise.jp/blog/mcp/
[31] https://licensecounter.jp/engineer-voice/blog/articles/20240404__netappai.html
[32] https://learn.microsoft.com/ja-jp/azure/azure-resource-manager/management/control-plane-and-data-plane
[33] https://www.ai-dounyu.com/articles/mcp
[34] https://github.com/modelcontextprotocol/specification/blob/main/schema/2025-03-26/schema.ts
[35] https://qiita.com/y-hirakaw/items/ec86741749eadcc71943
[36] https://azukiazusa.dev/blog/typescript-mcp-server
[37] https://www.linkedin.com/pulse/integrating-mcp-model-context-protocol-langchain4j-access-goncalves-pedze
[38] https://zenn.dev/smartround_dev/articles/d2050ff70a1311
[39] https://github.com/modelcontextprotocol/modelcontextprotocol
[40] https://zenn.dev/loglass/articles/320812a6629a45
[41] https://github.com/modelcontextprotocol
[42] https://crates.io/crates/mcp-schema
[43] https://modelcontextprotocol.io/introduction
[44] https://note.shiftinc.jp/n/n32d597411542
[45] https://github.com/modelcontextprotocol/servers
[46] https://modelcontextprotocol.io/docs/concepts/tools
[47] https://modelcontextprotocol.io/sdk/java/mcp-overview
[48] https://note.com/npaka/n/n4f7145cb9ad9
[49] https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization
[50] https://modelcontextprotocol.io/docs/concepts/transports
[51] https://zenn.dev/atamaplus/articles/5bf2bc1acef5b1
[52] https://qiita.com/nagix/items/712672a7bc741eef03aa
[53] https://engineering.mobalab.net/2025/04/21/connect-to-remote-mcp-server-from-claude-desktop-app-ja/
[54] https://times.serizawa.me/p/mcp-changelog-2025-03-26
[55] https://spec.modelcontextprotocol.io/specification/
[56] https://spec.modelcontextprotocol.io/specification/2024-11-05/server/tools/
[57] https://dev.classmethod.jp/articles/mcp-sse/

---
Perplexity の Eliot より: pplx.ai/share