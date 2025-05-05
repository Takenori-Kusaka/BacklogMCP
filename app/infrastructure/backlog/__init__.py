"""
Backlog APIとの連携を行うモジュール
"""
# テスト環境でのSSL検証スキップを有効にする場合は、
# 環境変数 BACKLOG_DISABLE_SSL_VERIFY=true を設定してください
from app.infrastructure.backlog.backlog_client_wrapper import BacklogClient
