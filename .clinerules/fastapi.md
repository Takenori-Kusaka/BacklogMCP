# FastAPI プロジェクト開発ルール集

## 目次

1. [プロジェクト構造](#1-プロジェクト構造)
2. [コード品質管理](#2-コード品質管理)
3. [開発環境](#3-開発環境)
4. [エンドポイント設計](#4-エンドポイント設計)
5. [依存性注入](#5-依存性注入)
6. [データベース連携](#6-データベース連携)
7. [テスト戦略](#7-テスト戦略)
8. [セキュリティ](#8-セキュリティ)
9. [パフォーマンス最適化](#9-パフォーマンス最適化)
10. [エラーハンドリングとロギング](#10-エラーハンドリングとロギング)
11. [環境変数と設定](#11-環境変数と設定)
12. [ドキュメント管理](#12-ドキュメント管理)
13. [デプロイメント](#13-デプロイメント)

## 1. プロジェクト構造

### 1.1 基本的なディレクトリ構造

```
my_fastapi_project/
│── app/
│   │── main.py           # アプリケーションのエントリーポイント
│   │── routers/          # ルーティングを分割するためのディレクトリ
│   │   │── __init__.py
│   │   │── user.py       # ユーザー関連のAPIルート
│   │   │── item.py       # アイテム関連のAPIルート
│   │── models/           # SQLAlchemyなどのモデル定義
│   │   │── __init__.py
│   │   │── user.py
│   │   │── item.py
│   │── schemas/          # Pydanticによるスキーマ定義
│   │   │── __init__.py
│   │   │── user.py
│   │   │── item.py
│   │── database.py       # データベース接続設定
│   │── dependencies.py   # 依存関係の管理
│   │── config.py         # 設定ファイル（環境変数など）
│   │── core/             # コアモジュール
│   │   │── logging.py    # ロギング設定
│   │   │── middleware/   # ミドルウェア
│   │      │── exception_handler.py
│── tests/                # テスト関連
│   │── test_main.py
│   │── conftest.py       # テスト用の共通fixture
│── .env                  # 環境変数
│── requirements.txt      # 必要なパッケージ
│── pyproject.toml        # プロジェクト設定
│── README.md             # プロジェクトの説明
│── Dockerfile            # Docker用の設定
│── docker-compose.yml    # Docker Compose設定
```

### 1.2 モジュール分割のベストプラクティス

- **関心の分離**: モデル、スキーマ、ルーターを明確に分けること[2]
- **初期化処理の分離**: `main.py`からの初期化処理を`init.py`に移動[6]
- **設定の一元管理**: 環境変数や設定は`config.py`に集約[7]
- **スケーラビリティ**: 小規模プロジェクトでも将来の拡張を考慮した構造設計[2]

## 2. コード品質管理

### 2.1 コード整形・静的解析ツール

```toml
# pyproject.toml の設定例
[tool.black]
line-length=120

[tool.flake8]
max-line-length=120
ignore=""
exclude=".venv/"

[tool.isort]
include_trailing_comma = true
line_length = 120
multi_line_output = 3
use_parentheses = true

[tool.mypy]
install_types = true
non_interactive = true
```

### 2.2 pre-commitの導入

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v2.3.0
  hooks:
    - id: check-yaml
    - id: end-of-file-fixer
    - id: trailing-whitespace
- repo: https://github.com/psf/black
  rev: 19.3b0
  hooks:
    - id: black
- repo: https://github.com/pycqa/flake8
  rev: 6.1.0
  hooks:
    - id: flake8
- repo: https://github.com/pycqa/isort
  rev: 5.12.0
  hooks:
    - id: isort
```

### 2.3 CI環境の構築

- GitHub Actionsを使ってテスト・リント・フォーマットを自動化[8]
- テスト用DBコンテナを利用したテスト環境の構築[8]
- コード品質チェックを自動化し、PRの品質を担保[8][9]

## 3. 開発環境

### 3.1 Dockerを活用した環境構築

```dockerfile
# Dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

```yaml
# docker-compose.yml
version: '3'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=fastapi_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  test_db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=test_db
    ports:
      - "5433:5432"

volumes:
  postgres_data:
```

### 3.2 依存パッケージ管理

- Poetryを使った依存関係管理[8]
- 本番環境と開発環境の依存関係を分離[8][14]

## 4. エンドポイント設計

### 4.1 標準的なルーティング構造

```python
# routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users
```

### 4.2 クエリパラメータのベストプラクティス

```python
from fastapi import FastAPI, Query

@app.get("/items/")
async def read_items(
    q: str | None = Query(default=None, max_length=50),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, le=100)
):
    return {"q": q, "skip": skip, "limit": limit}
```

- パラメータのバリデーションを適切に設定する[20]
- オプショナルパラメータにはデフォルト値を設定[20]
- 複数の値を受け取るクエリパラメータは配列で定義[20]

## 5. 依存性注入

### 5.1 データベースセッションの依存性注入

```python
# dependencies.py
from typing import Generator

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from .database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 5.2 認証と認可の依存性注入

```python
# dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    user = authenticate_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
```

### 5.3 依存関係のネスト

- 複雑な条件や前提条件を満たす依存性を構築[19]
- 共通ロジックを依存性として再利用[19]

## 6. データベース連携

### 6.1 SQLAlchemyによるモデル定義

```python
# models/user.py
from sqlalchemy import Column, Integer, String

from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
```

### 6.2 マイグレーション管理

```python
# alembic/env.py の設定
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.models import Base
from app.config import settings

# this is the Alembic Config object
config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata
```

### 6.3 トランザクション管理

- リクエストごとにセッション作成、終了時に閉じる[5]
- テスト時には自動ロールバックを利用[5]

## 7. テスト戦略

### 7.1 テスト構造

```
tests/
├── conftest.py          # 共通のフィクスチャ
├── test_users.py        # ユーザー関連のテスト
└── test_items.py        # アイテム関連のテスト
```

### 7.2 フィクスチャの活用

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.dependencies import get_db
from app.main import app

# テスト用DBの設定
SQLALCHEMY_TEST_DATABASE_URL = "postgresql://postgres:postgres@test_db:5432/test_db"

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
```

### 7.3 非同期テスト

```python
@pytest.mark.asyncio
async def test_create_user():
    # 非同期テストの実装
    pass
```

## 8. セキュリティ

### 8.1 認証

```python
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/secure-endpoint/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}
```

### 8.2 CORS設定

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://yourdomain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 8.3 CSRF対策

```python
from fastapi import FastAPI
from starlette_csrf import CSRFMiddleware

from config.csrf import csrf_settings

app = FastAPI()
app.add_middleware(CSRFMiddleware, **csrf_settings)
```

```python
# config/csrf.py
csrf_settings = {
    "secret": app_settings.SECRET_KEY,
    "exempt_urls": app_settings.EXCLUDED_PATHS,
    "cookie_name": "csrftoken",
    "cookie_secure": True,
    "cookie_httponly": True,
    "cookie_samesite": "Lax",
    "header_name": "x-csrftoken",
}
```

### 8.4 レート制限

```python
from fastapi import FastAPI, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
app = FastAPI()
app.state.limiter = limiter

@app.get("/limited-endpoint")
@limiter.limit("5/minute")
async def limited_endpoint(request: Request):
    return {"message": "This is a rate-limited endpoint"}
```

## 9. パフォーマンス最適化

### 9.1 非同期処理の活用

```python
@app.get("/async-endpoint")
async def read_async_data():
    result = await some_async_operation()
    return {"data": result}
```

### 9.2 モニタリングとパフォーマンス分析

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
    traces_sample_rate=1.0,
    integrations=[FastApiIntegration()]
)
```

### 9.3 N+1問題の解決

```python
# SQLAlchemyでのjoinedload使用例
from sqlalchemy.orm import joinedload

def get_users_with_items(db: Session):
    return db.query(User).options(joinedload(User.items)).all()
```

## 10. エラーハンドリングとロギング

### 10.1 ログ設定

```python
import logging
from logging.config import dictConfig
import os

# ログファイルディレクトリ設定
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'access_log': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 15,
            'filename': os.path.join(log_directory, 'access.log'),
            'formatter': 'default',
        },
        'error_log': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 15,
            'filename': os.path.join(log_directory, 'error.log'),
            'formatter': 'default',
        },
        'exception_log': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 15,
            'filename': os.path.join(log_directory, 'exception.log'),
            'formatter': 'default',
        }
    },
    'loggers': {
        'uvicorn.access': {
            'handlers': ['access_log'],
            'level': 'INFO',
            'propagate': False,
        },
        'uvicorn.error': {
            'handlers': ['error_log'],
            'level': 'INFO',
            'propagate': False,
        },
        'app.exception': {
            'handlers': ['exception_log'],
            'level': 'ERROR',
            'propagate': False,
        }
    }
}

# ロギング設定を適用
dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("app.exception")
```

### 10.2 例外ハンドラ

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )
```

## 11. 環境変数と設定

### 11.1 環境変数の読み込み

```python
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# .envファイルから環境変数を読み込む
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost:5432/db")
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "your-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS設定
    CORS_ORIGINS: list[str] = os.environ.get("CORS_ORIGINS", "http://localhost,http://localhost:3000").split(",")

    # 環境設定
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 11.2 環境別の設定

```bash
# .env.development
DATABASE_URL=postgresql://user:password@localhost:5432/dev_db
SECRET_KEY=dev_secret_key
ENVIRONMENT=development

# .env.production
DATABASE_URL=postgresql://user:password@db:5432/prod_db
SECRET_KEY=prod_secret_key
ENVIRONMENT=production
```

## 12. ドキュメント管理

### 12.1 API自動ドキュメント設定

```python
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    description="My FastAPI application",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
```

### 12.2 スキーマとレスポンスモデルの詳細な記述

```python
from pydantic import BaseModel, Field
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., description="ユーザー名", example="john_doe")
    email: str = Field(..., description="メールアドレス", example="john@example.com")
    password: str = Field(..., min_length=8, description="パスワード（8文字以上）")

class UserResponse(BaseModel):
    id: int = Field(..., description="ユーザーID")
    username: str = Field(..., description="ユーザー名")
    email: str = Field(..., description="メールアドレス")
    is_active: bool = Field(True, description="アクティブ状態")
    
    class Config:
        orm_mode = True
```

## 13. デプロイメント

### 13.1 本番環境用Dockerfileの最適化

```dockerfile
# 本番用Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target=/app/packages

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app/packages /app/packages
ENV PYTHONPATH=/app/packages
COPY ./app /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 13.2 デプロイ自動化

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches:
      - main

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      # テスト実行ステップ

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      # デプロイ用のステップ（環境によって異なる）
      # 例: AWS ECS, Kubernetes, Herokuなど
```

---

## ベストプラクティスの追加情報

1. **非同期処理を活用**: FastAPIはASGIフレームワークであり、非同期処理に対応しています。I/O待ちの多い処理はasync/awaitを活用しましょう[3]。

2. **型アノテーションを活用**: FastAPIはPydanticと型ヒントを使って自動バリデーションやドキュメント生成を行います。正確な型アノテーションを心がけましょう[16]。

3. **モジュールごとに責任範囲を明確に**: APIルート、データモデル、ビジネスロジックなど、それぞれの責任を明確に分けましょう[18]。

4. **環境変数に機密情報を格納**: パスワードやAPIキーなどの機密情報は環境変数で管理し、ソースコードには記載しないようにしましょう[7]。

5. **マイグレーションツールの活用**: データベーススキーマの変更はAlembicなどのマイグレーションツールを使って管理しましょう[13]。

6. **バージョン管理とセマンティックバージョニング**: APIにはバージョン番号を付け、互換性のない変更を行う場合は新しいバージョンを作成しましょう。

7. **継続的なモニタリングと改善**: Sentryなどのツールを活用して、パフォーマンスとエラーを継続的にモニタリングしましょう[15]。

8. **ドキュメントを常に最新に保つ**: FastAPIの自動ドキュメント生成機能を活用し、APIの変更はすぐにドキュメントに反映されるようにしましょう。

9. **セキュリティ対策の徹底**: CORS、CSRF、レート制限など、必要なセキュリティ対策を実装しましょう[10][11][12]。

10. **テストカバレッジの確保**: ユニットテスト、統合テスト、エンドツーエンドテストを組み合わせて、コードの品質を担保しましょう[5][8]。

Citations:
[1] https://zenn.dev/tk_resilie/books/bd5708c54a8a0a/viewer/00-introduction
[2] https://blog.greeden.me/2025/01/30/fastapi%E3%81%AE%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E6%A7%8B%E9%80%A0%E3%81%A8%E8%A8%AD%E8%A8%88%E6%99%82%E3%81%AE%E6%B3%A8%E6%84%8F%E7%82%B9/
[3] https://www.cfxlog.com/fastapi/
[4] https://fastapi.tiangolo.com/ja/tutorial/security/first-steps/
[5] https://qiita.com/Katsuya_Ogata/items/bf722219c2aa454bb0eb
[6] https://qiita.com/rom0323/items/2cde0ad7d9912b4e5f7f
[7] https://qiita.com/itinerant_programmer/items/756521ce572fb78d370f
[8] https://qiita.com/yuuki_0524/items/80006761f203c72bd6c5
[9] https://www.fastapitutorial.com/blog/fastapi-development-workflow/
[10] https://fastapi.tiangolo.com/ja/tutorial/cors/
[11] https://loadforge.com/guides/implementing-rate-limits-in-fastapi-a-step-by-step-guide
[12] https://qiita.com/shun198/items/17857bea62f873dedf14
[13] https://zenn.dev/satonopan/articles/4256417e6c629e
[14] https://qiita.com/kurodenwa/items/653c7b74f2f8ba5b7c0d
[15] https://qiita.com/nassy20/items/8979a6bc14a002fd43e7
[16] https://chocottopro.com/?p=670
[17] https://qiita.com/ikeike_ryuryu/items/ce92f1a650958b419bbb
[18] https://www.issoh.co.jp/tech/details/4347/
[19] https://zenn.dev/egg_glass/books/fastapi-for-starters/viewer/session
[20] https://apidog.com/jp/blog/fastapi-query-parameters-best-practices-jp/
[21] https://zenn.dev/noknmgc/articles/fastapi-directory-structure
[22] https://fastapi.tiangolo.com/ja/tutorial/
[23] https://chocottopro.com/?p=670
[24] https://dev.classmethod.jp/articles/fastapi-pytest/
[25] https://js2iiu.com/2025/02/18/python-lint-flake8-pylint-ruff-black/
[26] https://zenn.dev/fikastudio/articles/73c226000f9a0a
[27] https://blog.compliiant.io/api-defense-with-rate-limiting-using-fastapi-and-token-buckets-0f5206fc5029
[28] https://pypi.org/project/fastapi-csrf-protect/
[29] https://fastapi.tiangolo.com/ja/tutorial/background-tasks/
[30] https://blog.ojthon-dev.com/articles/ndrx96rn0hnq
[31] https://qiita.com/Katsuya_Ogata/items/bf722219c2aa454bb0eb
[32] https://zenn.dev/egg_glass/books/fastapi-for-starters/viewer/session
[33] https://www.issoh.co.jp/tech/details/3859/
[34] https://note.com/readytowork/n/n9cbbce77abc1
[35] https://www.genspark.ai/spark/next-js%E3%81%A8fastapi%E3%82%92%E7%94%A8%E3%81%84%E3%81%9Fapi%E8%AA%8D%E5%8F%AF%E3%81%AE%E3%83%99%E3%82%B9%E3%83%88%E3%83%97%E3%83%A9%E3%82%AF%E3%83%86%E3%82%A3%E3%82%B9/a20385b6-ca71-46e5-94de-6fb0b661ac8e
[36] https://zenn.dev/tk_resilie/articles/python_ruff_setup
[37] https://github.com/tiangolo/fastapi/issues/1522
[38] https://www.reddit.com/r/Python/comments/sbo2bs/flake8typechecking_now_has_support_for_fastapi/
[39] https://zenn.dev/horitaka/articles/python-formatter
[40] https://github.com/nnitiwe-dev/fastapi-cicd-demo
[41] https://qiita.com/rikuProgramer/items/7d311e87685a41823846
[42] https://zenn.dev/tk_resilie/books/bd5708c54a8a0a/viewer/00-introduction
[43] https://zenn.dev/crebo_tech/articles/article-0015-20241117
[44] https://note.com/engneer_hino/n/n1af0cdd7a4ff
[45] https://zenn.dev/shimi7o/articles/39a2b62fd7b1ac
[46] https://qiita.com/shun198/items/d5c23497318523899fae
[47] https://blog.fantom.co.jp/2023/12/05/fastapi-sqlalchemy-alembic-sqlite/
[48] https://blog.greeden.me/2025/04/09/python-fastapi-%E3%81%A7%E3%81%AE%E3%83%9E%E3%82%A4%E3%82%B0%E3%83%AC%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3%E7%AE%A1%E7%90%86%EF%BC%9Aalembic%E3%81%AE%E4%BD%BF%E3%81%84%E6%96%B9%E3%81%A8laravel/
[49] https://zenn.dev/katsu996/articles/python-fastapi

---
Perplexity の Eliot より: pplx.ai/share