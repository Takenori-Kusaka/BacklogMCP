"""
テスト用のロガー設定
"""
import logging
import os
from logging.handlers import RotatingFileHandler

# ログディレクトリの作成
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# ロガーの設定
def setup_logger(name, log_file, level=logging.DEBUG):
    """
    ロガーの設定
    
    Args:
        name: ロガー名
        log_file: ログファイル名
        level: ログレベル
        
    Returns:
        logging.Logger: 設定済みのロガー
    """
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # ファイルハンドラの設定
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, log_file),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'  # UTF-8エンコーディングを指定
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # コンソールハンドラの設定
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # ロガーの設定
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# テスト用のロガー
test_logger = setup_logger('test', 'test.log')
