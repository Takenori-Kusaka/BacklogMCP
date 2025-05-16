# Docker プロジェクト開発における包括的.clinerules ガイドライン

## イメージ構築最適化
### ビルドコンテキスト管理
不要ファイルの除外を厳格に実施するため、`.dockerignore`ファイルは必須とする[1][7]。特に`node_modules`、`.git`、ビルド成果物、ログファイルは明示的に除外する。ビルドコンテキストサイズは500MB未満に維持し、`.dockerignore`の更新をコミット前チェックリストに含める[7][20]。

マルチステージビルドを原則として採用し、ビルド環境と実行環境を分離する[1][8]。最終イメージには必要なランタイムとアプリケーションのみを含め、開発ツール類は中間ステージに限定する。Go言語の例:

```
# ビルドステージ
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /main

# 実行ステージ
FROM alpine:3.19
COPY --from=builder /main /main
CMD ["/main"]
```

### レイヤー最適化
`RUN`命令は論理的な単位で結合し、キャッシュ効率を最大化する[20]。パッケージインストール時はクリーンアップを同一レイヤーで実施:

```
RUN apt-get update && \
    apt-get install -y --no-install-recommends openssl && \
    rm -rf /var/lib/apt/lists/*
```

`COPY`/`ADD`命令は変更頻度の低いファイルから順に記述し、キャッシュヒット率を向上させる[1][20]。依存関係管理ファイル（`package.json`、`go.mod`など）はソースコードより先にコピーする。

## セキュリティ基準
### ベースイメージ管理
公式イメージを優先的に採用し、タグは明示的なバージョンを指定する[15][19]。Debian系イメージでは`slim`バリアントを基準とする:

```
FROM python:3.11-slim-bookworm
```

週次スキャンを実施し、CVEデータベースとの照合を自動化する[3][19]。Docker Scoutの統合例:

```
docker scout cves --exit-code --severity critical my-image:latest
```

### 権限最小化
rootユーザーでの実行を禁止し、非特権ユーザーを明示的に指定する[19][12]。ユーザー名前空間の再マップを有効化:

```
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser
```

Seccompプロファイルをカスタマイズし、不要なシステムコールをブロック[12][19]。AppArmor/SELinuxプロファイルの適用を必須とする。

## ネットワーク設計
### サービス分離
デフォルトブリッジネットワークの使用を禁止し、カスタムネットワークを定義して通信を制御[12][6]。サブネットとIP範囲を明示的に指定:

```
networks:
  backend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.28.0.0/24
```

サービス間通信はDNSベースのサービスディスカバリを採用し、静的IP依存を排除[6][12]。ヘルスチェックと組み合わせた例:

```
healthcheck:
  test: ["CMD", "curl", "-f", "http://db:3306"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## データ管理
### ボリューム設計
エフェメラルストレージを原則とし、永続化が必要なデータのみボリュームをマウント[13][19]。ファイルロックと排他制御を実装し、マルチインスタンスでのデータ破損を防止する。

バックアップ戦略としてResticを使用した暗号化バックアップを週次で実施:

```
docker run --rm -v appdata:/data -v backup:/backup restic/restic \
  backup /data --repo /backup/repo --password-file /secrets/restic-pass
```

## 運用監視
### ログ管理
`json-file`ログドライバの使用を禁止し、`local`ドライバでログローテーションを有効化[11][19]。ログ設定例:

```
{
  "log-driver": "local",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3",
    "compress": "true"
  }
}
```

### メトリクス収集
Prometheus用エンドポイントを公開し、cAdvisorと連携した監視を実装[6][10]。ヘルスチェック設定:

```
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

## CI/CD統合
### パイプライン設計
マルチアーキテクチャビルドをサポートするため、Buildxを必須ツールとして採用[20][3]。CI設定例:

```
- name: Build and push
  uses: docker/build-push-action@v4
  with:
    platforms: linux/amd64,linux/arm64
    tags: |
      my-registry/app:latest
      my-registry/app:${GIT_SHA}
```

### セキュリティスキャン
プッシュ前の脆弱性スキャンを必須化し、CRITICALレベルの脆弱性を検出した場合ビルドを失敗させる[3][19]:

```
- name: Scan image
  run: |
    docker scout cves --exit-code \
      --severity critical my-registry/app:${GIT_SHA}
```

## 開発者ワークフロー
### ローカル環境
開発用Compose設定ではホットリロードを有効化し、デバッグツールを統合[6][4]:

```
services:
  app:
    build: .
    volumes:
      - .:/app
      - /app/node_modules
    command: npm run dev
    environment:
      NODE_ENV: development
```

### テスト戦略
統合テスト用にテスト専用ネットワークを構築し、Testcontainersを活用した自動化を実施[6][10]:

```
@Testcontainers
class IntegrationTest {
    @Container
    static PostgreSQLContainer postgres = new PostgreSQLContainer<>("postgres:15");
}
```

## ドキュメンテーション
### Dockerfile規約
各Dockerfileの先頭にメタデータラベルを記載し、ビルド情報を追跡可能にする[14][18]:

```
LABEL org.opencontainers.image.title="My App" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.revision="${GIT_COMMIT}"
```

### ライフサイクル管理
イメージの有効期限（TTL）を設定し、未使用イメージの自動削除を実施[18][14]:

```
docker image prune --filter "until=72h" --force
```

## 例外処理
本ポリシーからの逸脱が必要な場合は、技術評議会での承認を必須とする。例外申請フォーマット:

```
### 例外申請書
- **対象コンポーネント**: 
- **申請理由**:
- **代替対策**:
- **有効期間**:
- **影響範囲分析**:
```

この.clinerulesはDocker公式ドキュメント[1][2]、OWASPコンテナセキュリティガイド[19]、CNCFベストプラクティス[12][13]を統合し、継続的に更新される。最新版は常にリポジトリの`.clinerules.md`を参照すること。

Citations:
[1] https://docs.docker.jp/develop/develop-images/dockerfile_best-practices.html
[2] https://docs.docker.jp/develop/dev-best-practices.html
[3] https://www.docker.com/ja-jp/resources/scout-cheat-sheet/
[4] https://qiita.com/Matsuy_org/items/5cc1ecf19bf2584744d9
[5] https://www.issoh.co.jp/tech/details/6033/
[6] https://dexall.co.jp/articles/?p=3376
[7] https://t-cr.jp/article/jsi1iq5b7obaarr
[8] https://matsuand.github.io/docs.docker.jp.onthefly/develop/develop-images/multistage-build/
[9] https://blog.gitguardian.com/how-to-handle-secrets-in-docker/
[10] https://lumigo.io/container-monitoring/docker-health-check-a-practical-guide/
[11] https://docs.docker.com/engine/logging/configure/
[12] https://www.creationline.com/tech-blog/tech-blog/cloudnative/aquasecurity/43087
[13] https://labex.io/ja/tutorials/docker-how-to-optimize-the-performance-of-docker-volumes-414916
[14] https://labex.io/ja/tutorials/docker-how-to-label-docker-containers-418917
[15] https://zenn.dev/forcia_tech/articles/20210716_docker_best_practice
[16] https://github.com/karaage0703/deep-novelist/blob/main/.clinerules
[17] https://qiita.com/umanetes/items/e0257dafb920726c4f94
[18] https://www.docker.com/ja-jp/blog/docker-best-practices-using-tags-and-labels-to-manage-docker-image-sprawl/
[19] https://kinsta.com/jp/blog/docker-security/
[20] https://www.docker.com/ja-jp/blog/intro-guide-to-dockerfile-best-practices/
[21] https://www.docker.com/ja-jp/blog/docker-for-web-developers/
[22] https://qiita.com/wMETAw/items/34ba5c980e2a38e548db
[23] https://bell-sw.com/blog/how-to-use-a-dockerfile-linter/
[24] https://github.com/hadolint/hadolint/blob/master/docker/README.md
[25] https://qiita.com/techneconn/items/6428b7a3bab1893499f0
[26] https://qiita.com/S4nTo/items/977d28b0eac316915702
[27] https://docs.docker.jp/develop/develop-images/multistage-build.html
[28] https://docs.docker.com/engine/swarm/secrets/
[29] https://www.reddit.com/r/docker/comments/x3c71s/docker_best_practice_host_or_bridge_network/?tl=ja
[30] https://t-cr.jp/article/pc61ipvlongvl9w
[31] https://zenn.dev/kusuke/articles/972fc135f85b86
[32] https://github.com/karaage0703/python-boilerplate
[33] https://qiita.com/negi0205/items/1d88a66bc46d58430f4a
[34] https://github.com/hadolint/hadolint
[35] https://zenn.dev/never_be_a_pm/scraps/f8889b60438b70
[36] https://qiita.com/himamura/items/f79deee7c66886c1e534
[37] https://genee.jp/contents/docker-compose/
[38] https://docs.docker.jp/get-started/08_using_compose.html
[39] https://y-ohgi.com/introduction-docker/4_tips/docker-compose/
[40] https://zenn.dev/yuukis234/articles/2c631cf73c40ba
[41] https://zenn.dev/forcia_tech/articles/20210716_docker_best_practice
[42] https://zenn.dev/hakshu/articles/docker-multi-stage-build
[43] https://qiita.com/minamijoyo/items/711704e85b45ff5d6405
[44] https://docs.docker.com/build/building/multi-stage/
[45] https://docs.docker.com/get-started/docker-concepts/building-images/multi-stage-builds/
[46] https://qiita.com/Toyo_m/items/52fa81948d5746dd2afc
[47] https://www.docker.com/ja-jp/blog/docker-engine-28-hardening-container-networking-by-default/
[48] https://matsuand.github.io/docs.docker.jp.onthefly/config/containers/container-networking/
[49] https://www.issoh.co.jp/tech/details/6033/

---
Perplexity の Eliot より: pplx.ai/share