"""
OpenAPI仕様書をYAML形式で生成するスクリプト
"""
import json
import yaml
import os
import sys
import requests
from pathlib import Path

def generate_openapi_yaml(output_dir: str = "docs", output_file: str = "openapi.yaml"):
    """
    FastAPIアプリケーションからOpenAPI仕様書をYAML形式で生成する
    
    Args:
        output_dir: 出力ディレクトリ
        output_file: 出力ファイル名
    """
    # 出力ディレクトリの作成
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # ローカルサーバーが起動していると仮定して、OpenAPI仕様を取得
        response = requests.get("http://localhost:8000/openapi.json")
        response.raise_for_status()
        openapi_json = response.json()
    except requests.RequestException as e:
        print(f"Error: ローカルサーバーからOpenAPI仕様を取得できませんでした: {e}")
        print("サーバーが起動していることを確認してください。")
        sys.exit(1)
    
    # JSONをYAMLに変換
    openapi_yaml = yaml.dump(openapi_json, sort_keys=False)
    
    # ファイルに保存
    output_path = Path(output_dir) / output_file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(openapi_yaml)
    
    print(f"OpenAPI仕様書を生成しました: {output_path}")
    return str(output_path)

if __name__ == "__main__":
    # コマンドライン引数から出力ディレクトリと出力ファイル名を取得
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "docs"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "openapi.yaml"
    
    generate_openapi_yaml(output_dir, output_file)
